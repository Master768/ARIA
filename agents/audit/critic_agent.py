import os
import ast
import json
import re
import logging
from typing import Optional, Dict, Any, List, Tuple

from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from agents.llm_client import GroqOllamaClient, get_llm
    from agents.data_science.data_agent import run_python_code, execute_sandbox_code
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient, get_llm
    from data_agent import run_python_code, execute_sandbox_code

log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
critic_logger = logging.getLogger("critic_agent")
critic_logger.setLevel(logging.INFO)


class ValidationResult:
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


from agents.audit.verification_pyramid import VerificationPyramidEngine

class CriticAgent:
    """Tier 4 Validation Intelligence: CriticAgent (Powered by 6-Layer Verification Pyramid)."""
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.client = GroqOllamaClient(host=host, model=model)
        self.llm = get_llm(model_name=model)
        self.model = model or os.getenv("GROQ_MODEL") or os.getenv("OLLAMA_MODEL") or "llama-3.3-70b-versatile"

    def validate(self, question: str, data_agent_result: Dict[str, Any], main_dataset: str, columns: list = None, prior_results: Optional[list] = None) -> ValidationResult:
        data_output_text = data_agent_result.get("output", "")
        data_agent_code = data_agent_result.get("code", "")

        # Run Verification Pyramid
        pyramid_audit = VerificationPyramidEngine.run_pyramid_audit(
            execution_result=data_agent_result,
            report_markdown=data_output_text
        )

        is_valid = pyramid_audit.get("overall_pass", True)
        status = "PASSED" if is_valid else "NEEDS_REFINEMENT"

        if not columns:
            columns = []
            try:
                import pandas as pd
                df_preview = pd.read_csv(main_dataset, nrows=2)
                columns = df_preview.columns.tolist()
            except Exception:
                pass

        system_instructions = (
            "You are a Critic Agent in an analytics validation team built on LangChain. "
            "Your job is to independently verify a data analytics finding by running Python code from scratch. "
            f"The dataset is local at '{main_dataset}'. Columns: {columns}"
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"Question: {question}\nClaimed result:\n{data_output_text}"}
        ]

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=[run_python_code]
            )
            tool_calls = response.message.tool_calls
            if tool_calls:
                code = tool_calls[0].function.arguments.get("code", "")
                output = execute_sandbox_code(code, "Critic verification code")
            else:
                code = ""
                output = response.message.content or ""
        except Exception as e:
            code = ""
            output = f"Critic execution failed: {e}"

        return ValidationResult(
            status=status,
            is_valid=is_valid,
            data_value=None,
            critic_value=None,
            diff=0.0,
            code=code,
            output=output
        )

CriticValidationResult = ValidationResult
