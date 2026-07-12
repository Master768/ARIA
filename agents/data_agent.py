import os
import json
import re
import logging
import subprocess
import time
from typing import Callable, List, Dict, Any, Optional
try:
    from agents.llm_client import GroqOllamaClient
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient
from dotenv import load_dotenv
try:
    from agents.debug_agent import DebugAgent, CodeExecutionError
except ModuleNotFoundError:
    from debug_agent import DebugAgent, CodeExecutionError

# Load env variables at startup
load_dotenv()

# Configure logger — file + console
log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)
if not _root_logger.handlers:
    # File handler
    _fh = logging.FileHandler(os.path.join(log_dir, "phase1.log"), encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    _root_logger.addHandler(_fh)
    # Console handler (INFO and above)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.WARNING)   # only warnings/errors on console; trace() handles INFO
    _ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _root_logger.addHandler(_ch)


def _trace(icon: str, msg: str) -> None:
    """Print a live status line to the console so the user can follow agent activity."""
    print(f"  {icon}  {msg}", flush=True)

def run_python_code(code: str, description: str = "") -> str:
    """
    Executes Python/pandas code inside a Docker container.
    Returns the stdout/stderr output from the execution.
    
    Args:
        code: The complete Python/Pandas code block to run.
        description: A short description of what the code checks.
    """
    # 1. Clean up and validate imports
    forbidden_imports = ['os', 'sys', 'subprocess', 'shutil', 'urllib', 'requests', 'socket', 'builtins.__import__']
    for imp in forbidden_imports:
        if f"import {imp}" in code or f"from {imp}" in code:
            return f"Security violation: Import of '{imp}' is forbidden."
            
    # Make sure sandbox dir exists
    sandbox_dir = os.path.abspath("sandbox")
    os.makedirs(sandbox_dir, exist_ok=True)
    
    temp_file_path = os.path.join(sandbox_dir, "temp_query.py")
    
    # Write the code to run
    # Ensure stdout is flushed and encoding is handled
    wrapped_code = f"""
import sys
# Make sure print output is flushed
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

{code}
"""
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(wrapped_code)
        
    try:
        use_docker = os.getenv("USE_DOCKER", "True").strip().lower() == "true"
        
        if use_docker:
            data_dir_abs = os.path.abspath("data").replace("\\", "/")
            sandbox_dir_abs = os.path.abspath("sandbox").replace("\\", "/")
            
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{data_dir_abs}:/workspace/data:ro",
                "-v", f"{sandbox_dir_abs}:/workspace/sandbox",
                "analytics-sandbox:latest",
                "python", "/workspace/sandbox/temp_query.py"
            ]
            
            use_fallback = False
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8")
                if result.returncode != 0 and ("docker: error during connect" in result.stderr or "docker: daemon" in result.stderr or "dockerDesktopLinuxEngine" in result.stderr or "No such file or directory" in result.stderr):
                    use_fallback = True
                else:
                    output = result.stdout
                    error = result.stderr
                    if result.returncode == 0:
                        return output if output.strip() else "Execution succeeded with no stdout."
                    else:
                        return f"Error (Exit Code {result.returncode}):\n{error}\nOutput:\n{output}"
            except (FileNotFoundError, subprocess.SubprocessError):
                use_fallback = True
        else:
            use_fallback = True

        if use_fallback:
            import sys
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                cwd=project_root
            )
            output = result.stdout
            error = result.stderr
            if result.returncode == 0:
                return output if output.strip() else "Execution succeeded with no stdout."
            else:
                return f"Error (Exit Code {result.returncode}):\n{error}\nOutput:\n{output}"
            
    except subprocess.TimeoutExpired:
        return "TimeoutExpired: Code execution exceeded 30 seconds limit."
    except Exception as e:
        return f"Execution failed: {str(e)}"
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

def _extract_inline_tool_call(content: str) -> Optional[Dict[str, Any]]:
    """
    Groq sometimes encodes tool calls as a raw XML-style string inside message
    content instead of using the tool_calls field, e.g.:
        <function/run_python_code>{"code": "...", "description": "..."}</function>
    This helper detects and parses that pattern, returning the arguments dict
    or None if the pattern is not found.
    """
    if not content:
        return None
    # Match <function/TOOL_NAME>{...}</function> or <function/TOOL_NAME>{...}
    pattern = r'<function/run_python_code>(.*?)(?:</function>|$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        raw_json = match.group(1).strip()
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            pass
    return None


class DataAgent:
    def __init__(self, host: str = None, model: str = None, debug_agent: Optional[Any] = None):
        self.client = GroqOllamaClient(host=host, model=model)
        self.debug_agent = debug_agent

        if not model:
            # Default to GROQ_MODEL or OLLAMA_MODEL based on configuration
            model = os.getenv("GROQ_MODEL") or os.getenv("OLLAMA_MODEL") or "llama-3.3-70b-versatile"

        self.model = model

    def ask_question(self, question: str, prior_results: Optional[list] = None) -> dict:
        """
        Executes an agentic loop to answer the question using the run_python_code tool.
        Includes single-attempt error repair.
        """
        logging.info(f"Received query: {question}")
        _trace("🧠", f"Data Agent received query: {question[:120]}{'...' if len(question) > 120 else ''}")
        
        # Discover all CSV files in data/ and select the best match for this question.
        # Strategy: score each file by (a) exact name match, (b) token match against filename,
        # (c) column-name overlap with question keywords — whichever scores highest wins.
        data_files = []
        try:
            data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
        except:
            pass

        # Financial / OHLCV keywords that indicate the crypto/price dataset
        FINANCIAL_KEYWORDS = {
            "volume", "price", "close", "open", "high", "low", "ohlc", "ohlcv",
            "candle", "candlestick", "trade", "btc", "bitcoin", "crypto",
            "binance", "usdt", "eth", "ema", "sma", "rsi", "macd",
            "bullish", "bearish", "breakout", "support", "resistance",
            "sharpe", "drawdown", "return", "pnl", "strategy", "backtest"
        }
        # Telecom / churn keywords
        CHURN_KEYWORDS = {
            "churn", "customer", "telecom", "monthly charges", "contract",
            "tenure", "internet service", "phone service", "payment method"
        }

        question_lower = question.lower()

        def _score_file(filename: str) -> int:
            score = 0
            name_no_ext = os.path.splitext(filename)[0].lower()
            # Exact file name match
            if name_no_ext in question_lower or filename.lower() in question_lower:
                score += 100
            # Token overlap with filename
            tokens = name_no_ext.replace("_", " ").replace("-", " ").split()
            for tok in tokens:
                if len(tok) >= 3 and tok in question_lower:
                    score += 20
            # Column-name overlap: peek at headers
            try:
                import pandas as pd
                header = pd.read_csv(os.path.join("data", filename), nrows=0).columns.str.lower().tolist()
                for col in header:
                    if col in question_lower:
                        score += 10
                # Bonus: if question contains financial words AND file has OHLCV-like columns
                has_financial_cols = any(c in header for c in ["close", "open", "high", "low", "volume"])
                has_churn_cols = any(c in header for c in ["churn", "customerid", "tenure"])
                q_financial = any(kw in question_lower for kw in FINANCIAL_KEYWORDS)
                q_churn = any(kw in question_lower for kw in CHURN_KEYWORDS)
                if has_financial_cols and q_financial:
                    score += 50
                if has_churn_cols and q_churn:
                    score += 50
            except Exception:
                pass
            return score

        if data_files:
            scored = sorted(data_files, key=_score_file, reverse=True)
            selected_file = scored[0] if _score_file(scored[0]) > 0 else data_files[0]
        else:
            selected_file = None

        if selected_file:
            main_dataset = f"data/{selected_file}"
        else:
            main_dataset = "data/telco_churn.csv"

        _trace("📂", f"Dataset selected: {main_dataset}")

        columns = []
        sample_data = ""
        try:
            import pandas as pd
            df_preview = pd.read_csv(main_dataset, nrows=2)
            columns = df_preview.columns.tolist()
            # Truncate very long string values to keep system prompt readable and compact
            df_preview = df_preview.map(lambda x: str(x)[:80] + "..." if isinstance(x, str) and len(x) > 80 else x)
            sample_data = df_preview.to_string(index=False)
        except Exception:
            pass

        _trace("📋", f"Columns available: {columns if columns else '(will read after load)'}")
        
        # Build prior context block for derived sub-tasks (differences, % changes, etc.)
        prior_context = ""
        if prior_results:
            prior_context = "\n\nContext from prior verified sub-tasks (use these EXACT values when computing derived metrics like % change, difference, ratio — do NOT recompute from scratch):\n"
            for r in prior_results:
                prior_context += f"  - Sub-task {r['id']} ({r['query']}): {r['output'].strip()}\n"
            prior_context += "\n"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Data Agent in an analytics team. "
                    "Your job is to answer the user's data question by generating and running Pandas code. "
                    "You must ALWAYS run code to verify your answers using the run_python_code tool. "
                    "Do NOT estimate or guess answers without running code. "
                    f"The local CSV files are located in 'data/'. The main dataset is '{main_dataset}'. "
                    f"The columns in this dataset are: {columns}\n"
                    f"Here is a sample (first 3 rows) of the dataset to see formatting and values:\n"
                    f"{sample_data}\n\n"
                    f"To read the data, always use relative path: pd.read_csv('{main_dataset}'). "
                    "Ensure your code print()s the final numeric answers so they are captured in stdout.\n"
                    "Date filtering rules:\n"
                    "- ALWAYS use na=False when calling str.contains() to avoid NaN masking errors: df[df['Date'].str.contains('2025', na=False)]\n"
                    "- Do NOT convert the Date column to datetime and back to string just for filtering — use str.contains() directly on the raw string column.\n"
                    "- If you must parse dates, use pd.to_datetime(df['Date'], format='mixed', errors='coerce') and filter with .dt.year, .dt.month etc.\n"
                    "- If a 'Unix' column is present, it may contain mixed units (milliseconds like 1.7e12 or microseconds like 1.7e15). Convert them safely using: df['Unix'] = np.where(df['Unix'] > 1e14, df['Unix'] / 1000, df['Unix']); pd.to_datetime(df['Unix'], unit='ms')\n\n"
                    "CRITICAL: Do NOT import 'os', 'sys', 'subprocess', or any forbidden libraries. "
                    "Importing them will trigger a security violation and cause the run to fail. "
                    "Always load the dataset directly using pd.read_csv without checking file existence first."
                    + prior_context
                )
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        # 1. Initial LLM call
        _trace("🤖", "Calling LLM to generate analysis code...")
        response = None
        for attempt in range(3):
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=[run_python_code]
                )
                break
            except Exception as e:
                err_msg = f"Failed to query LLM: {str(e)}"
                logging.warning(f"LLM query attempt {attempt+1} failed: {err_msg}")
                if attempt < 2:
                    logging.info("Sleeping 5s before retrying LLM query...")
                    time.sleep(5.0)
                else:
                    logging.error("Max LLM query attempts reached.")
                    return {"status": "error", "code": "", "output": err_msg}

        # 2. Check if model decided to call tool
        tool_calls = response.message.tool_calls

        # Groq sometimes encodes tool calls as raw XML text in content instead
        # of the tool_calls field. Detect and parse that pattern.
        if not tool_calls:
            inline_args = _extract_inline_tool_call(response.message.content or "")
            if inline_args:
                logging.info("Detected inline function call in content. Extracting tool args.")
                _trace("🔧", "Detected inline function call — extracting tool args from response text.")
                # Duck-typed wrapper — no import needed, the pipeline only accesses .function.name / .function.arguments
                class _InlineToolCall:
                    class function:
                        name = "run_python_code"
                        arguments = inline_args
                tool_calls = [_InlineToolCall()]
            else:
                logging.warning("Model answered directly without calling the execution tool.")
                return {
                    "status": "warning",
                    "code": "# No code executed (Direct answer)",
                    "output": response.message.content
                }

        tool_call = tool_calls[0]
        code = tool_call.function.arguments.get("code", "")
        description = tool_call.function.arguments.get("description", "")

        logging.info(f"Data Agent generated code:\n{code}")
        _trace("⚡", "Executing generated code in sandbox...")

        # Run code in sandbox
        result = run_python_code(code, description)
        logging.info(f"Sandbox output:\n{result}")

        # Show a compact preview of execution output
        preview = result.strip().splitlines()
        if preview:
            _trace("📤", f"Sandbox output ({len(preview)} lines): {preview[0][:120]}{'...' if len(preview) > 1 else ''}")
        else:
            _trace("⚠️ ", "Sandbox returned no output.")
        
        # 3. If execution failed (e.g. contains traceback or "Error"), run self-correction/debug loop
        is_error = (
            "Error" in result or 
            "Traceback" in result or 
            "Exception" in result or 
            "TimeoutExpired" in result or 
            "Security violation" in result or
            result.strip() == "Execution succeeded with no stdout."
        )
        
        debug_used = False
        debug_attempts = 0
        debug_details = []
        
        if is_error:
            if self.debug_agent:
                logging.info("[DataAgent] Invoking Debug Agent...")
                _trace("🐞", "Execution failed — invoking Debug Agent for auto-repair...")
                # Parse error type and message
                error_type = "RuntimeError"
                error_message = result
                lines = result.splitlines()
                for line in reversed(lines):
                    if ":" in line and not line.startswith(" ") and any(ext in line for ext in ["Error", "Exception", "KeyError", "TypeError", "ValueError", "IndexError", "Security violation"]):
                        parts = line.split(":", 1)
                        error_type = parts[0].strip()
                        error_message = parts[1].strip()
                        break
                
                error = CodeExecutionError(
                    error_type=error_type,
                    error_message=error_message,
                    traceback=result,
                    code_executed=code,
                    execution_time_ms=0.0
                )
                
                debug_result = self.debug_agent.handle_error(error, question)
                self.debug_agent.log_debug_session(debug_result)
                
                debug_used = True
                debug_attempts = len(debug_result.attempts)
                debug_details = [
                    {
                        "attempt": a.attempt_number,
                        "error": f"{a.original_error.error_type}: {a.original_error.error_message}",
                        "fix": a.fix_explanation
                    }
                    for a in debug_result.attempts
                ]
                
                if debug_result.status == "FIXED":
                    logging.info("[DataAgent] ✓ Debug Agent fixed the error")
                    _trace("✅", f"Debug Agent fixed the error on attempt {debug_attempts}.")
                    code = debug_result.final_code
                    result = debug_result.final_result
                else:
                    logging.error(f"[DataAgent] ✗ Debug Agent couldn't fix: {debug_result.escalation_reason}")
                    _trace("❌", f"Debug Agent failed after {debug_attempts} attempts: {debug_result.escalation_reason}")
                    return {
                        "status": "FAILED_AFTER_DEBUG",
                        "error": error_message,
                        "debug_attempts": debug_attempts,
                        "debug_details": debug_details,
                        "debug_used": True,
                        "code": code,
                        "output": f"Error: {debug_result.escalation_reason}"
                    }
            else:
                logging.warning("Execution failed. Triggering basic self-correction loop.")
                # Build a simple correction conversation that doesn't rely on
                # tool_call_id round-trips (avoids Groq 400 on malformed multi-turn).
                correction_messages = [
                    messages[0],   # system prompt
                    messages[1],   # original user question
                    {
                        "role": "assistant",
                        "content": (
                            f"I tried to answer with this code:\n```python\n{code}\n```\n"
                            f"But it failed with the following error:\n{result}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "The code above returned an error. "
                            "Please fix it, correct any syntax or logic mistakes, "
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
                        logging.info(f"Self-correction generated code:\n{code}")
                        result = run_python_code(code, "Fixed code execution")
                        logging.info(f"Self-correction sandbox output:\n{result}")
                    else:
                        logging.warning("Self-correction failed to generate a tool call.")
                        result = repair_response.message.content
                except Exception as e:
                    result = f"Self-correction query failed: {str(e)}"
                    logging.error(result)

        _trace("💬", "Generating natural language summary from execution output...")
        # 4. Final summary generation.
        # IMPORTANT: Always embed the literal execution output in the prompt so the
        # model cannot claim it has no output. If the model still gives a non-answer,
        # fall back to the raw result string directly.
        summary_messages = [
            *messages,
            {
                "role": "assistant",
                "content": (
                    f"I executed the following code:\n```python\n{code}\n```\n"
                    f"The execution produced this exact output:\n\n{result}\n\n"
                    "Use only the numbers and data printed above to answer the question."
                )
            },
            {
                "role": "user",
                "content": (
                    "Based ONLY on the execution output shown above, provide a concise answer to my question. "
                    "Quote the specific numbers from the output. Do NOT say you lack the output — it is shown above."
                )
            }
        ]

        try:
            final_summary = self.client.chat(
                model=self.model,
                messages=summary_messages
            )
            summary_content = final_summary.message.content
            # Guard: if the model still claims no output or gives a code block instead of an answer, use raw result
            bad_summary_signals = [
                "i don't have the execution output",
                "i don't have access",
                "please run this code",
                "let me try again",
                "```python",
            ]
            if not summary_content or not summary_content.strip() or any(
                sig in summary_content.lower() for sig in bad_summary_signals
            ):
                summary_content = result
        except Exception as e:
            # Fallback: surface the raw execution output rather than failing silently
            summary_content = f"(Summary failed: {str(e)}) Raw output:\n{result}"
            
        logging.info(f"Final summary:\n{summary_content}")
        
        return {
            "status": "success" if not debug_used or result != "Error" else "SUCCESS_WITH_DEBUG",
            "code": code,
            "output": summary_content,
            "debug_used": debug_used,
            "debug_attempts": debug_attempts,
            "debug_details": debug_details
        }

def _read_multiline_input(prompt: str) -> str:
    """
    Reads multi-line input from stdin.
    The user signals end-of-question by entering a blank line or typing END.
    This lets users paste multi-line questions without each line being processed separately.
    """
    print(prompt)
    print("  (Paste your question across multiple lines, then press Enter on a blank line to submit. Type 'exit' to quit.)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            # Piped input — treat EOF as end of question
            break
        stripped = line.strip()
        if stripped.lower() == "exit":
            return "exit"
        if stripped.lower() == "end" or (not stripped and lines):
            # Blank line after content = submit; lone blank line = ignore
            break
        lines.append(line)
    return "\n".join(lines).strip()


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    agent = DataAgent()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}")
        res = agent.ask_question(question)
        print("\n--- CODE EXECUTED ---")
        print(res["code"])
        print("\n--- ANSWER ---")
        print(res["output"])
    else:
        print("Data Agent interactive mode.")
        while True:
            try:
                question = _read_multiline_input("\nAsk a question:")
                if question.lower() == "exit":
                    break
                if not question:
                    continue
                print("Processing...")
                res = agent.ask_question(question)
                print("\n--- CODE EXECUTED ---")
                print(res["code"])
                print("\n--- ANSWER ---")
                print(res["output"])
            except KeyboardInterrupt:
                print("\nExiting.")
                break

