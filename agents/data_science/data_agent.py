import os
import sys
import json
import re
import logging
import subprocess
import time
from typing import Callable, List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from agents.llm_client import GroqOllamaClient, get_llm
    from agents.engineering.debug_agent import DebugAgent, CodeExecutionError
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient, get_llm
    from debug_agent import DebugAgent, CodeExecutionError

log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)

def _trace(icon: str, msg: str) -> None:
    try:
        print(f"  {icon}  {msg}", flush=True)
    except UnicodeEncodeError:
        safe_msg = msg.encode('ascii', 'replace').decode('ascii')
        print(f"  [*]  {safe_msg}", flush=True)


def execute_sandbox_code(code: str, description: str = "") -> str:
    forbidden_imports = ['sys', 'subprocess', 'shutil', 'urllib', 'requests', 'socket', 'builtins.__import__']
    for imp in forbidden_imports:
        if f"import {imp}" in code or f"from {imp}" in code:
            return f"Security violation: Import of '{imp}' is forbidden."
            
    sandbox_dir = os.path.abspath("sandbox")
    os.makedirs(sandbox_dir, exist_ok=True)
    temp_file_path = os.path.join(sandbox_dir, "temp_query.py")
    
    wrapped_code = f"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

{code}
"""
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(wrapped_code)
        
    try:
        use_docker = os.getenv("USE_DOCKER", "False").strip().lower() == "true"
        
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
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8")
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
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=120,
                encoding="utf-8",
                cwd=project_root
            )
            output = result.stdout
            error = result.stderr
            if result.returncode == 0:
                return output if output.strip() else "Execution succeeded with no stdout."
            else:
                return f"Error (Exit Code {result.returncode}):\n{error}\nOutput:\n{error}"
            
    except subprocess.TimeoutExpired:
        return "TimeoutExpired: Code execution exceeded 120 seconds limit."
    except Exception as e:
        return f"Execution failed: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass


@tool
def run_python_code(code: str, description: str = "") -> str:
    """
    Executes Python/pandas code inside a Docker container or sandbox.
    Returns the stdout/stderr output from the execution.
    """
    return execute_sandbox_code(code, description)


def _extract_inline_tool_call(content: str) -> Optional[Dict[str, Any]]:
    if not content:
        return None
    pattern = r'<function/run_python_code>(.*?)(?:</function>|<function/run_python_code>|$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        raw_str = match.group(1).strip()
        json_match = re.search(r'\{.*\}', raw_str, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
    code_match = re.search(r"```(?:python)?\s*\n?(.*?)```", content, re.DOTALL)
    if code_match:
        return {"code": code_match.group(1).strip(), "description": "Extracted code block"}
    return None


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

from agents.skills.skill_registry import SkillRegistry

class DataAgent:
    """Tier 2 Code Intelligence: DataAgent (Host Container for Dynamic Skill Plugins)."""
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None, debug_agent: Optional[Any] = None):
        self.client = GroqOllamaClient(host=host, model=model)
        self.llm = get_llm(model_name=model)
        self.debug_agent = debug_agent
        self.model = model or os.getenv("GROQ_MODEL") or os.getenv("OLLAMA_MODEL") or "llama-3.3-70b-versatile"
        self.skill_registry = SkillRegistry(auto_discover=True)

    def ask_question(self, question: str, prior_results: Optional[list] = None) -> dict:
        logging.info(f"Received query: {question}")
        _trace("🧠", f"Data Agent received query: {question[:120]}{'...' if len(question) > 120 else ''}")
        
        # Dynamic Skill Plugin Discovery & Resolution
        resolved_skills = self.skill_registry.resolve_best_skills(question, top_k=2)
        if resolved_skills:
            skill_names = ", ".join([f"'{s.name}' ({s.category})" for s in resolved_skills])
            _trace("🧩", f"DataAgent dynamically loaded Skill Plugin(s): {skill_names}")
        
        data_dir = os.path.join(PROJECT_ROOT, "data")
        data_files = []
        try:
            data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        except:
            pass

        question_lower = question.lower()
        core_question_lower = question_lower.split("context retrieved from vector")[0]
        question_words = set(re.findall(r'[a-zA-Z0-9_]+', core_question_lower))

        def _score_file(filename: str) -> int:
            score = 0
            filename_lower = filename.lower()
            name_no_ext = os.path.splitext(filename)[0].lower()
            if filename_lower in core_question_lower or name_no_ext in core_question_lower:
                score += 1000
            tokens = name_no_ext.replace("_", " ").replace("-", " ").split()
            for tok in tokens:
                if len(tok) >= 3 and tok in question_words:
                    score += 20
            return score

        sandbox_cleaned_csv = os.path.join(PROJECT_ROOT, "sandbox", "cleaned_dataset.csv")
        if os.path.exists(sandbox_cleaned_csv):
            main_dataset = sandbox_cleaned_csv
        elif data_files:
            scored = sorted(data_files, key=_score_file, reverse=True)
            selected_file = scored[0] if _score_file(scored[0]) > 0 else data_files[0]
            main_dataset = os.path.join(data_dir, selected_file)
        else:
            main_dataset = None

        if not main_dataset or not os.path.exists(main_dataset):
            return {
                "status": "warning",
                "code": "# No dataset available in data/ directory",
                "output": "No dataset files found in data/ directory. Please upload or add a CSV file to data/."
            }

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

        prior_context_str = ""
        if prior_results:
            prior_context_str = "\n\nUPSTREAM NODE VERIFIED FACTS (MAINTAIN CONSISTENCY):\n" + "\n".join([f"- {res}" for res in prior_results[:3]])

        system_prompt = (
            "You are a Data Agent in an analytics team built on LangChain. "
            "Your job is to answer the user's data question by generating and running Pandas code. "
            "You must ALWAYS run code to verify your answers using the run_python_code tool. "
            f"The local dataset is at '{main_dataset}'. "
            f"The columns in this dataset are: {columns}\n"
            f"Sample rows:\n{sample_data}"
            f"{prior_context_str}\n\n"
            f"Always pd.read_csv('{main_dataset}'). Print final answers.\n"
            "IMPORTANT FOR PLOTS: When generating heatmaps or scatter plots, select at most 10 numeric columns (e.g. df.select_dtypes(include=['number']).columns[:10]) for sub-second rendering.\n"
            "STATE CONSISTENCY REQUIREMENT: If your query filters rows (e.g. by position, stage, or outlier removal), state your filter explicitly in stdout (e.g. 'Filtered dataset to position: Defender')."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
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
                if attempt == 2:
                    return {"status": "error", "code": "", "output": str(e)}

        tool_calls = response.message.tool_calls
        if not tool_calls:
            inline_args = _extract_inline_tool_call(response.message.content or "")
            if inline_args:
                class _InlineToolCall:
                    class function:
                        name = "run_python_code"
                        arguments = inline_args
                tool_calls = [_InlineToolCall()]
            else:
                return {
                    "status": "warning",
                    "code": "# Direct answer",
                    "output": response.message.content
                }

        tool_call = tool_calls[0]
        code = tool_call.function.arguments.get("code", "")
        description = tool_call.function.arguments.get("description", "")

        result = execute_sandbox_code(code, description)
        
        is_error = "Error" in result or "Traceback" in result or "Exception" in result
        
        if is_error and self.debug_agent:
            error = CodeExecutionError(
                error_type="RuntimeError",
                error_message=result,
                traceback=result,
                code_executed=code,
                execution_time_ms=0.0
            )
            debug_res = self.debug_agent.handle_error(error, question)
            if debug_res.status == "FIXED":
                code = debug_res.final_code
                result = debug_res.final_result

        return {
            "status": "success",
            "code": code,
            "output": result,
            "sandbox_output": result
        }
