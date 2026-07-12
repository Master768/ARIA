import json
import traceback
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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

class DebugAgentOutput(BaseModel):
    task_id: int
    original_question: str
    status: str  # FIXED, FAILED_MAX_RETRIES, ESCALATED
    attempts: List[DebugAttempt]
    final_result: Optional[str] = None
    final_code: Optional[str] = None
    escalation_reason: Optional[str] = None
    timestamp: str

class DebugAgent:
    def __init__(self, llm_client, model: str, sandbox_run_fn, max_retries=3):
        """
        Args:
            llm_client: LLM client (GroqOllamaClient or compatible)
            model: Model name for LLM
            sandbox_run_fn: Standalone execution function run_python_code
            max_retries: Maximum number of fix attempts
        """
        self.llm = llm_client
        self.model = model
        self.sandbox_run_fn = sandbox_run_fn
        self.max_retries = max_retries
        self.retry_count = 0
    
    def handle_error(self, 
                    error: CodeExecutionError, 
                    original_question: str,
                    task_id: int = 0) -> DebugAgentOutput:
        """
        Main entry point when code execution fails
        """
        self.retry_count = 0
        attempts = []
        current_error = error
        
        logger.info(f"[DebugAgent] Starting error recovery for task {task_id}")
        logger.info(f"[DebugAgent] Error: {error.error_type} - {error.error_message}")
        
        while self.retry_count < self.max_retries:
            self.retry_count += 1
            logger.info(f"[DebugAgent] Attempt {self.retry_count}/{self.max_retries}")
            
            # Step 1: Analyze error
            analysis = self._analyze_error(current_error)
            logger.info(f"[DebugAgent] Analysis: {analysis}")
            
            # Step 2: Propose fix
            proposed_code = self._propose_fix(
                original_question,
                current_error,
                analysis,
                attempts
            )
            logger.info(f"[DebugAgent] Proposed fix:\n{proposed_code}")
            
            # Step 3: Test fix
            result = self._test_fix(proposed_code)
            
            # Step 4: Record attempt
            attempt = DebugAttempt(
                attempt_number=self.retry_count,
                original_error=current_error,
                proposed_fix=proposed_code,
                fix_explanation=analysis.get('explanation', analysis.get('fix_approach', 'Propose fix')),
                execution_result=result.get('output'),
                success=result['success']
            )
            attempts.append(attempt)
            
            # Step 5: Check if fixed
            if result['success']:
                logger.info(f"[DebugAgent] ✓ Error fixed on attempt {self.retry_count}")
                return DebugAgentOutput(
                    task_id=task_id,
                    original_question=original_question,
                    status="FIXED",
                    attempts=attempts,
                    final_result=result['output'],
                    final_code=proposed_code,
                    timestamp=datetime.now().isoformat()
                )
            
            # Update error for next iteration
            current_error = result['error']
            logger.warning(f"[DebugAgent] Fix attempt {self.retry_count} failed: {current_error.error_type}")
        
        # Max retries reached
        logger.error(f"[DebugAgent] Max retries ({self.max_retries}) exceeded")
        return DebugAgentOutput(
            task_id=task_id,
            original_question=original_question,
            status="FAILED_MAX_RETRIES",
            attempts=attempts,
            escalation_reason=f"Failed to fix after {self.max_retries} attempts",
            timestamp=datetime.now().isoformat()
        )
    
    def _analyze_error(self, error: CodeExecutionError) -> dict:
        """Classify and understand the error using LLM"""
        prompt = f"""
Analyze this code execution error and provide structured analysis:

Error Type: {error.error_type}
Error Message: {error.error_message}
Traceback (last 3 lines): {error.traceback.splitlines()[-3:] if error.traceback else ""}

Code that failed:
```python
{error.code_executed}
```

Respond with a JSON object containing:
{{
    "classification": "One of: [schema_error, type_error, timeout, memory_error, logic_error, other]",
    "root_cause": "Why this error occurred (be specific)",
    "affected_part": "Which line/section caused the error",
    "schema_issue": "If applicable, what data/column issue caused it",
    "fix_approach": "How to fix this error",
    "explanation": "Clear explanation of the fix strategy",
    "confidence": 0.0-1.0
}}

Be concise and technical. Return ONLY the JSON object. Do not wrap in markdown or code blocks.
"""
        try:
            response = self.llm.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0}
            )
            content = response.message.content.strip()
            
            # Clean up markdown code wrapping if model included it
            if content.startswith("```"):
                lines = content.splitlines()
                if len(lines) > 2:
                    content = "\n".join(lines[1:-1])
                    if content.startswith("json"):
                        content = content[4:].strip()
            
            analysis = json.loads(content)
        except Exception as e:
            logger.warning(f"LLM error analysis failed: {str(e)}. Using fallback.")
            analysis = {
                "classification": "other",
                "root_cause": error.error_message,
                "fix_approach": "Rewrite code with standard fixes",
                "explanation": "Original code execution failed",
                "confidence": 0.5
            }
        
        return analysis
    
    def _propose_fix(self, 
                    original_question: str,
                    error: CodeExecutionError,
                    analysis: dict,
                    previous_attempts: List[DebugAttempt]) -> str:
        """Generate corrected code"""
        attempt_history = ""
        if previous_attempts:
            attempt_history = "Previous failed attempts:\n"
            for attempt in previous_attempts:
                attempt_history += f"\n- Attempt {attempt.attempt_number}: {attempt.fix_explanation}\n"
                attempt_history += f"  Error: {attempt.original_error.error_type}\n"
        
        prompt = f"""
Fix this code error.

Original Question: "{original_question}"

Failed Code:
```python
{error.code_executed}
```

Error Analysis:
- Classification: {analysis.get('classification', 'unknown')}
- Root Cause: {analysis.get('root_cause', 'Unknown')}
- Fix Approach: {analysis.get('fix_approach', 'Rewrite')}
- Explanation: {analysis.get('explanation', '')}

{attempt_history}

Generate CORRECTED pandas/Python code that:
1. Fixes the identified issue
2. Does NOT repeat previous mistakes
3. Includes basic error handling (try/except for critical operations)
4. Adds data validation (check dtypes, nulls, missing columns)
5. Follows pandas best practices

Return ONLY the corrected code, no explanations or markdown wrappers.
"""
        try:
            response = self.llm.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0}
            )
            fixed_code = response.message.content.strip()
            
            # Clean up markdown code wrapping if present
            if fixed_code.startswith("```"):
                lines = fixed_code.splitlines()
                if len(lines) > 2:
                    fixed_code = "\n".join(lines[1:-1])
                    if fixed_code.startswith("python"):
                        fixed_code = fixed_code[6:].strip()
            elif "```python" in fixed_code:
                # Extract block between ```python and ```
                parts = fixed_code.split("```python")
                if len(parts) > 1:
                    fixed_code = parts[1].split("```")[0].strip()
        except Exception as e:
            logger.error(f"LLM fix proposal failed: {str(e)}.")
            fixed_code = error.code_executed
        
        return fixed_code.strip()
    
    def _test_fix(self, code: str) -> dict:
        """Execute the proposed fix in sandbox"""
        try:
            result = self.sandbox_run_fn(code, "Debug Agent retry")
            is_error = (
                "Error" in result or 
                "Traceback" in result or 
                "Exception" in result or 
                "TimeoutExpired" in result or 
                "Security violation" in result or
                result.strip() == "Execution succeeded with no stdout."
            )
            
            if is_error:
                # Try to parse error type
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
                return {
                    'success': False,
                    'error': error
                }
            else:
                return {
                    'success': True,
                    'output': result
                }
        except Exception as e:
            error = CodeExecutionError(
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc(),
                code_executed=code,
                execution_time_ms=0.0
            )
            return {
                'success': False,
                'error': error
            }
    
    def log_debug_session(self, output: DebugAgentOutput, log_file: str = "logs/debug_agent.log"):
        """Log debug session for audit trail"""
        log_entry = {
            "timestamp": output.timestamp,
            "task_id": output.task_id,
            "original_question": output.original_question,
            "status": output.status,
            "attempts": len(output.attempts),
            "success": output.status == "FIXED",
            "attempts_detail": [
                {
                    "attempt": a.attempt_number,
                    "error_type": a.original_error.error_type,
                    "fix_explanation": a.fix_explanation,
                    "success": a.success
                }
                for a in output.attempts
            ],
            "escalation_reason": output.escalation_reason
        }
        
        try:
            import os
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a', encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            logger.info(f"[DebugAgent] Session logged: {log_entry}")
        except Exception as e:
            logger.error(f"[DebugAgent] Failed to log session: {str(e)}")
