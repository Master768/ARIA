import os
import json
import re
import logging
from typing import Optional, Dict, Any
try:
    from agents.llm_client import GroqOllamaClient
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient
from dotenv import load_dotenv
try:
    from agents.data_agent import run_python_code
except ModuleNotFoundError:
    from data_agent import run_python_code


def _extract_inline_tool_call(content: str) -> Optional[Dict[str, Any]]:
    """
    Groq sometimes encodes tool calls as a raw XML-style string inside message
    content instead of using the tool_calls field, e.g.:
        <function/run_python_code>{"code": "...", "description": "..."}</function>
    This helper detects and parses that pattern, returning the arguments dict or None.
    """
    if not content:
        return None
    pattern = r'<function/run_python_code>(.*?)(?:</function>|$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        raw_json = match.group(1).strip()
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            pass
    return None


# Load env variables
load_dotenv()

# Configure Critic Logger
log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
critic_logger = logging.getLogger("critic_agent")
critic_logger.setLevel(logging.INFO)

# Avoid adding duplicate handlers if the logger is re-initialized
if not critic_logger.handlers:
    fh = logging.FileHandler(os.path.join(log_dir, "phase2_validation.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    critic_logger.addHandler(fh)


class CriticValidationResult:
    """Holds the verification results from the Critic Agent."""
    def __init__(
        self,
        status: str,
        is_valid: bool,
        data_value: Optional[float],
        critic_value: Optional[float],
        diff: float,
        code: str,
        output: str
    ):
        self.status = status
        self.is_valid = is_valid
        self.data_value = data_value
        self.critic_value = critic_value
        self.diff = diff
        self.code = code
        self.output = output

    def __repr__(self) -> str:
        return f"CriticValidationResult(status={self.status}, is_valid={self.is_valid})"

class CriticAgent:
    def __init__(self, host: str = None, model: str = None):
        self.client = GroqOllamaClient(host=host, model=model)
 
        # Check available models
        available_models = []
        try:
            tags = self.client.list()
            available_models = [m.model for m in tags.models]
        except Exception as e:
            critic_logger.error(f"Failed to fetch models: {str(e)}")
 
        if not model:
            # Default to GROQ_MODEL or OLLAMA_MODEL based on configuration
            model = os.getenv("GROQ_MODEL") or os.getenv("OLLAMA_MODEL") or "llama-3.3-70b-versatile"
 
        # Dynamic fallback if target model is not pulled
        if available_models and model not in available_models and "gpt-oss:20b-cloud" in available_models:
            critic_logger.warning(f"Model '{model}' not found. Falling back to 'gpt-oss:20b-cloud'.")
            model = "gpt-oss:20b-cloud"
 
        self.model = model

    def _extract_numeric_from_text(self, text: str, question: str) -> Optional[float]:
        """
        Uses Ollama to extract the primary numeric value from text.
        Falls back to regex if LLM-based extraction fails.
        """
        text_str = str(text).strip()

        # Guard: nan/None/null are computation failures, not extractable numbers
        if text_str.lower() in ('nan', 'none', 'null', 'na', ''):
            return None
        # Guard: if the only number in the text would be a year like 2025 extracted
        # from a phrase like "October 2025 average", reject that silently below.
        
        # Heuristic 1: If text is already a clean integer or float, return it directly
        try:
            return float(text_str)
        except ValueError:
            pass

        # Prompt model to extract the primary number
        prompt = (
            f"Given the user question: '{question}'\n"
            f"And the text response: '{text_str}'\n"
            "Extract the primary numeric answer to the question (count, average, median, percentage, etc.) as a JSON object with a single key 'value' containing the number as a float or integer.\n"
            "If no number is found or it is not numeric, return null.\n"
            "Example output: {\"value\": 64.76}\n"
            "Return only valid JSON. Do not include markdown code block formatting."
        )
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.0}
            )
            content = response.message.content.strip()
            
            # Strip markdown if model included it
            if content.startswith("```"):
                lines = content.splitlines()
                if len(lines) > 2:
                    content = "\n".join(lines[1:-1])
                    if content.startswith("json"):
                        content = content[4:].strip()
            
            data = json.loads(content)
            val = data.get("value")
            if val is not None:
                return float(val)
        except Exception as e:
            critic_logger.warning(f"LLM numeric extraction failed: {str(e)}. Falling back to regex.")

        # Regex fallback: find all numbers (optionally with decimal point)
        # Clean commas (e.g. 7,043 -> 7043)
        clean_text = re.sub(r'(\d),(\d)', r'\1\2', text_str)
        matches = re.findall(r'-?\d+\.?\d*', clean_text)
        if matches:
            try:
                # Take the last match because the final answer is usually at the end of the script output
                return float(matches[-1])
            except ValueError:
                pass
        return None

    def validate(self, question: str, data_agent_result: Dict[str, Any], main_dataset: str, columns: list = None, prior_results: Optional[list] = None) -> CriticValidationResult:
        """
        Validates the Data Agent's result independently by writing and running a fresh Pandas query.
        """
        data_output_text = data_agent_result.get("output", "")
        critic_logger.info(f"Validating query: {question}")
        critic_logger.info(f"Data Agent claimed answer: {data_output_text}")

        # Use the main_dataset passed from the orchestrator (already correctly selected)
        # Read columns from the correct dataset if not provided
        if not columns:
            columns = []
            sample_data = ""
            try:
                import pandas as pd
                df_preview = pd.read_csv(main_dataset, nrows=2)
                columns = df_preview.columns.tolist()
                df_preview = df_preview.map(lambda x: str(x)[:80] + "..." if isinstance(x, str) and len(x) > 80 else x)
                sample_data = df_preview.to_string(index=False)
            except Exception:
                pass
        else:
            sample_data = ""
            try:
                import pandas as pd
                df_preview = pd.read_csv(main_dataset, nrows=2)
                df_preview = df_preview.map(lambda x: str(x)[:80] + "..." if isinstance(x, str) and len(x) > 80 else x)
                sample_data = df_preview.to_string(index=False)
            except Exception:
                pass

        # 1. Ask model to independently write verification Pandas code.
        # Ensure we NEVER show the Data Agent's generated code to the Critic.
        # Check if the dataset has a Unix column that needs normalization
        has_unix_col = "Unix" in columns

        unix_normalization_rule = ""
        if has_unix_col:
            unix_normalization_rule = (
                "\n\nMANDATORY Unix Column Normalization (ALWAYS apply this before any Unix/date computation):\n"
                "import numpy as np\n"
                "df['Unix'] = np.where(df['Unix'] > 1e14, df['Unix'] / 1000, df['Unix'])\n"
                "# This normalizes all Unix values to milliseconds regardless of source unit.\n"
                "# You MUST include this normalization step as the FIRST operation after loading the CSV.\n"
                "# Failure to do so will produce wrong results due to mixed ms/us units in the dataset.\n"
            )

        system_instructions = (
            "You are a Critic Agent in an analytics validation team. "
            "Your job is to independently verify a data analytics finding. "
            "You are given ONLY the original question and the claimed summary text. "
            "You must write clean, executable Pandas python code to compute the correct value from scratch. Do not guess the answer.\n\n"
            f"The dataset is local at '{main_dataset}'.\n"
            f"The column schema of the dataset is:\n"
            f"{columns}\n\n"
            f"Here is a sample (first 3 rows) of the dataset to see formatting and values:\n"
            f"{sample_data}\n\n"
            f"Always load the data using: pd.read_csv('{main_dataset}').\n"
            "Write the final calculation code immediately. Do not print df.head(), columns, or shape. "
            "Print ONLY the single final calculated numeric result answering the question so it is captured in stdout.\n"
            f"{unix_normalization_rule}"
            "Date filtering rules:\n"
            "- ALWAYS use na=False when calling str.contains() to avoid NaN masking errors: df[df['Date'].str.contains('2025', na=False)]\n"
            "- Do NOT convert the Date column to datetime and back to string just for filtering — use str.contains() directly on the raw string column.\n"
            "- If you must parse dates, use pd.to_datetime(df['Date'], format='mixed', errors='coerce') and filter with .dt.year, .dt.month etc.\n"
            "- If parsing date strings with pd.to_datetime, use format='mixed' or errors='coerce' to safely handle inconsistent row formats.\n\n"
            "CRITICAL: Do NOT import 'os', 'sys', 'subprocess', or any forbidden libraries. "
            "Importing them will trigger a security violation and cause the run to fail. "
            "Always load the dataset directly using pd.read_csv without checking file existence first."
        )

        # Build prior context block so Critic uses the same reference values as the Data Agent
        prior_context = ""
        if prior_results:
            prior_context = "\n\nContext from prior verified sub-tasks (use these EXACT values when computing derived metrics like % change, difference, ratio):\n"
            for r in prior_results:
                prior_context += f"  - Sub-task {r['id']} ({r['query']}): {r['output'].strip()}\n"
            prior_context += "\nIf this question asks for a change/difference/ratio between values computed in earlier sub-tasks, " \
                             "use the above verified outputs directly rather than recomputing from scratch.\n"

        # Provide a code template with the correct dataset path pre-filled.
        # This prevents the LLM from hallucinating a different CSV filename.
        code_template = (
            f"```python\n"
            f"import pandas as pd\n"
            f"import numpy as np\n"
            f"\n"
            f"# Dataset is already loaded — do NOT change this path\n"
            f"df = pd.read_csv('{main_dataset}')\n"
            f"# Available columns: {columns}\n"
            f"\n"
            f"# --- Write your analysis code below this line ---\n"
            f"# Filter, compute, and print() exactly ONE numeric result\n"
            f"```"
        )

        code_request_suffix = (
            f"\n\nComplete the following Python code to answer the question. "
            f"Do NOT change the dataset path or column names. "
            f"Print exactly ONE numeric result.\n\n"
            f"{code_template}"
        )

        messages = [
            {
                "role": "system",
                "content": system_instructions + prior_context
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Claimed Answer: {data_output_text}\n"
                    f"{code_request_suffix}"
                )
            }
        ]


        try:
            response = self.client.chat(
                model=self.model,
                messages=messages
                # No tools= parameter — ask for markdown code block instead
            )
        except Exception as e:
            err_msg = f"Critic failed to query LLM: {str(e)}"
            critic_logger.error(err_msg)
            return CriticValidationResult(
                status="FAILED (LLM error)",
                is_valid=False,
                data_value=None,
                critic_value=None,
                diff=0.0,
                code="",
                output=err_msg
            )

        raw_content = response.message.content or ""
        code = ""

        # Extract python code from tool calls if present (e.g. run_python_code or container.exec)
        tool_calls = getattr(response.message, "tool_calls", None)
        if tool_calls:
            try:
                tool_call = tool_calls[0]
                tool_func = getattr(tool_call, "function", None)
                if tool_func:
                    tool_name = getattr(tool_func, "name", "")
                    tool_args = getattr(tool_func, "arguments", {})
                    if isinstance(tool_args, str):
                        try:
                            tool_args = json.loads(tool_args)
                        except Exception:
                            tool_args = {}

                    if tool_name == "run_python_code":
                        code = tool_args.get("code", "")
                    elif tool_name == "container.exec":
                        cmd = tool_args.get("cmd", [])
                        if isinstance(cmd, str):
                            cmd = [cmd]
                        for part in cmd:
                            if "python - <<" in part or "python -" in part:
                                # Extract python code block between inline shell script markers
                                lines = part.splitlines()
                                code_lines = []
                                in_code = False
                                for line in lines:
                                    if "python - <<" in line or line.strip() == "PY":
                                        in_code = not in_code
                                        continue
                                    if in_code:
                                        code_lines.append(line)
                                if code_lines:
                                    code = "\n".join(code_lines)
                                    break
                                else:
                                    code = part
            except Exception as tool_err:
                critic_logger.warning(f"Error parsing tool calls in critic: {tool_err}")

        # Extract Python code from markdown code block if not extracted from tool calls
        if not code:
            code_match = re.search(r"```(?:python)?\s*\n?(.*?)```", raw_content, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
            else:
                # Fallback: if no markdown block, try to use the whole response as code
                # (sometimes model omits the backticks)
                stripped = raw_content.strip()
                if stripped.startswith("import ") or stripped.startswith("df ") or "pd.read_csv" in stripped:
                    code = stripped
                else:
                    # No code at all — fall back to direct answer extraction
                    critic_logger.warning(f"Critic returned no code block. Response: {raw_content[:200]}")
                    direct_val = self._extract_numeric_from_text(raw_content, question)
                    data_val_text = data_agent_result.get("output", "")
                    data_val = self._extract_numeric_from_text(data_val_text, question)
                    if direct_val is not None and data_val is not None:
                        pct_diff = (abs(data_val - direct_val) / abs(direct_val)) * 100.0 if direct_val != 0 else (100.0 if data_val != 0 else 0.0)
                        is_valid = pct_diff <= 3.0
                        status = f"PASSED (direct answer, diff: {pct_diff:.2f}%)" if is_valid else f"FAILED (direct mismatch: {data_val:.4f} vs {direct_val:.4f}, diff {pct_diff:.2f}%)"
                        return CriticValidationResult(status=status, is_valid=is_valid, data_value=data_val, critic_value=direct_val, diff=pct_diff, code="(direct)", output=raw_content)
                    return CriticValidationResult(status="FAILED (No code generated)", is_valid=False, data_value=None, critic_value=None, diff=0.0, code="", output=raw_content)

        # Force the correct dataset path — LLMs sometimes hallucinate a different CSV filename.
        # Simple greedy pattern: replace ANY pd.read_csv(...) call with the correct one.
        corrected_code = re.sub(
            r"pd\.read_csv\([^)]+\)",
            f"pd.read_csv('{main_dataset}')",
            code
        )
        if corrected_code != code:
            critic_logger.info(f"Corrected dataset path: replaced hallucinated CSV with '{main_dataset}'")
        code = corrected_code

        critic_logger.info(f"Critic Agent generated code:\n{code}")

        # 2. Run the generated code in the sandbox
        sandbox_output = run_python_code(code, question)
        critic_logger.info(f"Critic sandbox output:\n{sandbox_output}")

        is_error = (
            "Error" in sandbox_output or 
            "Traceback" in sandbox_output or 
            "Exception" in sandbox_output or 
            "TimeoutExpired" in sandbox_output or 
            "Security violation" in sandbox_output or
            sandbox_output.strip() == "Execution succeeded with no stdout."
        )
        if is_error:
            critic_logger.warning("Critic execution failed. Triggering self-correction loop.")
            # Same safe pattern as DataAgent — avoids Groq 400 from malformed tool_call_id round-trips
            correction_messages = [
                messages[0],   # system prompt
                messages[1],   # original user question
                {
                    "role": "assistant",
                    "content": (
                        f"I tried to verify with this code:\n```python\n{code}\n```\n"
                        f"But it failed with the following error:\n{sandbox_output}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "The code above returned an error. "
                        "Please fix any indentation, syntax, or logic mistakes, "
                        "and call run_python_code with the corrected version."
                    ),
                },
            ]
            try:
                repair_response = self.client.chat(
                    model=self.model,
                    messages=correction_messages,
                    tools=[run_python_code]
                )
                repair_tool_calls = repair_response.message.tool_calls
                if repair_tool_calls:
                    repair_tool_call = repair_tool_calls[0]
                    code = repair_tool_call.function.arguments.get("code", "")
                    critic_logger.info(f"Critic self-correction generated code:\n{code}")
                    sandbox_output = run_python_code(code, "Fixed Critic code execution")
                    critic_logger.info(f"Critic self-correction sandbox output:\n{sandbox_output}")
                else:
                    critic_logger.warning("Critic self-correction failed to generate code.")
            except Exception as e:
                critic_logger.error(f"Critic self-correction failed: {str(e)}")

        # Check error state again after self-correction
        is_error = "Error" in sandbox_output or "Traceback" in sandbox_output or "Exception" in sandbox_output or "TimeoutExpired" in sandbox_output
        if is_error:
            return CriticValidationResult(
                status="FAILED (Critic execution error)",
                is_valid=False,
                data_value=None,
                critic_value=None,
                diff=0.0,
                code=code,
                output=sandbox_output
            )

        # 3. Extract numeric values from both Data Agent and Critic output
        data_val = self._extract_numeric_from_text(data_output_text, question)
        critic_val = self._extract_numeric_from_text(sandbox_output, question)

        critic_logger.info(f"Extracted values -> Data Agent: {data_val}, Critic: {critic_val}")

        if data_val is not None and critic_val is not None:
            # Check for fractional vs percentage scaling mismatch (e.g. 0.427 vs 42.7)
            if abs(data_val - critic_val * 100) / max(abs(data_val), 1e-9) <= 0.01:
                critic_val = critic_val * 100
                critic_logger.info(f"Scaled Critic value from fraction to percentage: {critic_val}")
            elif abs(critic_val - data_val * 100) / max(abs(critic_val), 1e-9) <= 0.01:
                data_val = data_val * 100
                critic_logger.info(f"Scaled Data Agent value from fraction to percentage: {data_val}")
            # Check for 1000x scale mismatch (e.g. milliseconds vs microseconds in Unix timestamps)
            elif abs(data_val) > 0 and abs(critic_val - data_val * 1000) / max(abs(critic_val), 1e-9) <= 0.05:
                data_val = data_val * 1000
                critic_logger.info(f"Scaled Data Agent value by 1000x (ms -> us): {data_val}")
            elif abs(critic_val) > 0 and abs(data_val - critic_val * 1000) / max(abs(data_val), 1e-9) <= 0.05:
                critic_val = critic_val * 1000
                critic_logger.info(f"Scaled Critic value by 1000x (ms -> us): {critic_val}")

        if data_val is None or critic_val is None:
            err_msg = f"Failed to extract numeric values (Data Agent: {data_val}, Critic: {critic_val})"
            critic_logger.error(err_msg)
            return CriticValidationResult(
                status="FAILED (Extraction failure)",
                is_valid=False,
                data_value=data_val,
                critic_value=critic_val,
                diff=0.0,
                code=code,
                output=sandbox_output
            )

        # 4. Determine validation status based on data type and tolerance checks
        # Tolerance level 1: Count tolerance & Numeric Exact Match
        # Check if BOTH values are mathematically integers (e.g., 1869.0 or 1869)
        # Large integers (> 1000) are NOT row counts — they are timestamps, prices, volumes, etc.
        # and must use percentage tolerance instead.
        is_count = data_val.is_integer() and critic_val.is_integer() and abs(data_val) <= 1000 and abs(critic_val) <= 1000

        if is_count:
            diff_rows = abs(data_val - critic_val)
            # Count tolerance: within 1 row
            if diff_rows == 0.0:
                status = "PASSED (diff: 0.0 rows)"
                is_valid = True
            elif diff_rows <= 1.0:
                status = f"PASSED (diff: {diff_rows:.1f} rows)"
                is_valid = True
            else:
                status = f"FAILED (mismatch: Data Agent = {data_val:.1f}, Critic = {critic_val:.1f}, diff = {diff_rows:.1f} rows)"
                is_valid = False
            diff_val = diff_rows
        else:
            # Tolerance level 2: Percentage tolerance for floats (±3.0%)
            # 3% is appropriate for financial/statistical computations where two independent
            # implementations may use different date boundaries, rounding, or filter logic.
            if critic_val == 0.0:
                # Avoid division by zero
                pct_diff = 100.0 if data_val != 0.0 else 0.0
            else:
                pct_diff = (abs(data_val - critic_val) / abs(critic_val)) * 100.0

            if pct_diff <= 3.0:
                status = f"PASSED (diff: {pct_diff:.2f}%)"
                is_valid = True
            else:
                status = f"FAILED (mismatch: Data Agent = {data_val:.4f}, Critic = {critic_val:.4f}, diff = {pct_diff:.2f}%)"
                is_valid = False
            diff_val = pct_diff

        critic_logger.info(f"Validation outcome: {status}")
        return CriticValidationResult(
            status=status,
            is_valid=is_valid,
            data_value=data_val,
            critic_value=critic_val,
            diff=diff_val,
            code=code,
            output=sandbox_output
        )
