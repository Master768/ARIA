import os
import ast
import json
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from agents.llm_client import get_llm
    from agents.engineering.debug_classifier import ErrorClassifier, ErrorCategory
    from agents.engineering.debug_root_cause import RootCauseAnalyzer
    from agents.engineering.debug_patcher import DeterministicPatchEngine
    from agents.engineering.debug_validator import DebugValidatorAndMemory
except ModuleNotFoundError:
    from llm_client import get_llm
    from debug_classifier import ErrorClassifier, ErrorCategory
    from debug_root_cause import RootCauseAnalyzer
    from debug_patcher import DeterministicPatchEngine
    from debug_validator import DebugValidatorAndMemory

logger = logging.getLogger("debug_agent")

class CodeExecutionError(BaseModel):
    error_type: str
    error_message: str
    traceback: str
    code_executed: str
    execution_time_ms: float

class DebugAttempt(BaseModel):
    attempt_number: int
    original_error: CodeExecutionError
    proposed_fix: str
    fix_explanation: str
    execution_result: Optional[str] = None
    success: bool
    confidence_score: float = 1.0

class DebugAgentOutput(BaseModel):
    task_id: int
    original_question: str
    status: str
    attempts: List[DebugAttempt]
    final_result: Optional[str] = None
    final_code: Optional[str] = None
    escalation_reason: Optional[str] = None
    timestamp: str


class EnterpriseDebugAgent:
    """Tier 3 Engineering Debugger Agent."""
    def __init__(self, llm_client=None, model: Optional[str] = None, sandbox_run_fn=None, max_retries: int = 3):
        if isinstance(llm_client, BaseChatModel):
            self.llm = llm_client
        elif llm_client is not None:
            self.llm = llm_client
        else:
            self.llm = get_llm(model_name=model)

        self.model = model or "gpt-oss:20b-cloud"
        self.sandbox_run_fn = sandbox_run_fn
        self.max_retries = max_retries
        self.validator_memory = DebugValidatorAndMemory()

    def handle_error(
        self,
        error: CodeExecutionError,
        original_question: str,
        task_id: int = 0
    ) -> DebugAgentOutput:
        category, max_retries = ErrorClassifier.classify(error.traceback, error.error_message)

        csv_match = re.search(r"pd\.read_csv\([\'\"](.*?)[\'\"]\)", error.code_executed)
        dataset_path = csv_match.group(1) if csv_match else None

        analysis = RootCauseAnalyzer.analyze(error.code_executed, error.traceback, dataset_path=dataset_path)

        memory_fix = self.validator_memory.get_memory_fix(category.value, analysis.get("failing_line", error.error_message))
        if memory_fix:
            is_ast_valid, _ = self.validator_memory.validate_ast(memory_fix)
            if is_ast_valid:
                out = self.sandbox_run_fn(memory_fix, "Memory Fix Execution")
                is_reg_valid, _ = self.validator_memory.verify_no_regression("", out)
                if is_reg_valid:
                    attempt = DebugAttempt(
                        attempt_number=1,
                        original_error=error,
                        proposed_fix=memory_fix,
                        fix_explanation="Applied verified fix from SHA-256 Failure Memory Store (0 LLM calls)",
                        execution_result=out,
                        success=True,
                        confidence_score=0.99
                    )
                    return DebugAgentOutput(
                        task_id=task_id,
                        original_question=original_question,
                        status="FIXED",
                        attempts=[attempt],
                        final_result=out,
                        final_code=memory_fix,
                        timestamp=datetime.now().isoformat()
                    )

        det_result = DeterministicPatchEngine.try_deterministic_patch(error.code_executed, category.value, analysis)
        if det_result:
            patched_code, expl, confidence = det_result
            is_ast_valid, _ = self.validator_memory.validate_ast(patched_code)
            if is_ast_valid:
                out = self.sandbox_run_fn(patched_code, "Deterministic Patch Execution")
                is_reg_valid, _ = self.validator_memory.verify_no_regression("", out)
                if is_reg_valid:
                    self.validator_memory.save_memory_fix(category.value, analysis.get("failing_line", error.error_message), patched_code)
                    attempt = DebugAttempt(
                        attempt_number=1,
                        original_error=error,
                        proposed_fix=patched_code,
                        fix_explanation=expl,
                        execution_result=out,
                        success=True,
                        confidence_score=confidence
                    )
                    return DebugAgentOutput(
                        task_id=task_id,
                        original_question=original_question,
                        status="FIXED",
                        attempts=[attempt],
                        final_result=out,
                        final_code=patched_code,
                        timestamp=datetime.now().isoformat()
                    )

        attempts = []
        retry_count = 0
        while retry_count < max_retries:
            retry_count += 1
            patched_code = self._generate_llm_targeted_patch(original_question, error, analysis)
            
            is_ast_valid, ast_err = self.validator_memory.validate_ast(patched_code)
            if not is_ast_valid:
                continue

            out = self.sandbox_run_fn(patched_code, f"LLM Patch Candidate {retry_count}")
            is_reg_valid, reg_msg = self.validator_memory.verify_no_regression("", out)

            if is_reg_valid:
                self.validator_memory.save_memory_fix(category.value, analysis.get("failing_line", error.error_message), patched_code)
                attempt = DebugAttempt(
                    attempt_number=retry_count,
                    original_error=error,
                    proposed_fix=patched_code,
                    fix_explanation="LLM line-level targeted diff patch verified successfully",
                    execution_result=out,
                    success=True,
                    confidence_score=0.90
                )
                attempts.append(attempt)
                return DebugAgentOutput(
                    task_id=task_id,
                    original_question=original_question,
                    status="FIXED",
                    attempts=attempts,
                    final_result=out,
                    final_code=patched_code,
                    timestamp=datetime.now().isoformat()
                )

        return DebugAgentOutput(
            task_id=task_id,
            original_question=original_question,
            status="FAILED_MAX_RETRIES",
            attempts=attempts,
            escalation_reason=f"Exceeded category retry limit ({max_retries})",
            timestamp=datetime.now().isoformat()
        )

    def _generate_llm_targeted_patch(self, question: str, error: CodeExecutionError, analysis: Dict[str, Any]) -> str:
        prompt_text = (
            f"Original Question: '{question}'\n"
            f"Failing Line {analysis.get('failing_line_num')}: `{analysis.get('failing_line')}`\n"
            f"Error Message: {error.error_message}\n"
            f"Full Code:\n```python\n{error.code_executed}\n```\n\n"
            "Provide corrected Python code in a single ```python block."
        )

        try:
            if hasattr(self.llm, "chat"):
                res = self.llm.chat(model=self.model, messages=[{"role": "user", "content": prompt_text}])
                content = getattr(getattr(res, "message", res), "content", "")
            else:
                prompt_template = ChatPromptTemplate.from_messages([("user", "{prompt_text}")])
                chain = prompt_template | self.llm
                res = chain.invoke({"prompt_text": prompt_text})
                content = getattr(res, "content", str(res))

            match = re.search(r"```(?:python)?\s*\n?(.*?)```", content, re.DOTALL)
            return match.group(1).strip() if match else error.code_executed
        except Exception:
            return error.code_executed

    def log_debug_session(self, output: DebugAgentOutput):
        try:
            log_file = os.path.abspath("logs/debug_sessions.json")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            sessions = []
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
            sessions.append(output.dict())
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2)
        except Exception:
            pass

DebugAgent = EnterpriseDebugAgent
