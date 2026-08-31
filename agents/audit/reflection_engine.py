import logging
from typing import Dict, Any, List, Optional, Callable
from agents.audit.verification_pyramid import VerificationPyramidEngine

logger = logging.getLogger("reflection_engine")

class ReflectionEngine:
    """
    Deep Research Reflection Engine.
    Executes the autonomous iteration loop:
    Generate -> Execute -> Reflect -> What failed? -> Improve -> Re-execute -> Compare -> Publish
    """

    def __init__(self, max_iterations: int = 3, target_score_threshold: float = 0.80):
        self.max_iterations = max_iterations
        self.target_score_threshold = target_score_threshold

    def execute_with_reflection(
        self,
        task_query: str,
        execution_fn: Callable[[str, Optional[str]], Dict[str, Any]],
        improve_prompt_fn: Optional[Callable[[str, List[str]], str]] = None,
        dataset_intel: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs the full iterative Reflection Loop until quality threshold is met or max_iterations reached.
        """
        iterations_history: List[Dict[str, Any]] = []
        current_prompt = task_query
        best_candidate: Optional[Dict[str, Any]] = None
        best_score = -1.0

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"[ReflectionEngine] Iteration {iteration}/{self.max_iterations} - Executing...")
            
            # Step 1: Generate & Execute
            exec_result = execution_fn(task_query, current_prompt)
            
            # Step 2: Reflect & Validate via Verification Pyramid
            summary_stats = exec_result.get("summary_stats")
            generated_files = exec_result.get("generated_files", [])
            report_markdown = exec_result.get("report_markdown", "")

            audit = VerificationPyramidEngine.run_pyramid_audit(
                execution_result=exec_result,
                report_markdown=report_markdown,
                summary_stats=summary_stats,
                generated_files=generated_files,
                dataset_intel=dataset_intel
            )

            score = audit.get("overall_score", 0.0)
            issues = audit.get("all_issues", [])

            iteration_record = {
                "iteration": iteration,
                "prompt": current_prompt,
                "execution_result": exec_result,
                "audit": audit,
                "score": score,
                "issues": issues
            }
            iterations_history.append(iteration_record)

            logger.info(f"[ReflectionEngine] Iteration {iteration} Score: {score:.4f} (Pass: {audit.get('overall_pass')})")

            if score > best_score:
                best_score = score
                best_candidate = iteration_record

            # Check if threshold met
            if score >= self.target_score_threshold and len(issues) == 0:
                logger.info(f"[ReflectionEngine] Quality threshold reached on iteration {iteration}!")
                break

            # Step 3: What failed? & Improve
            if iteration < self.max_iterations:
                feedback = self._diagnose_failures(issues, audit)
                if improve_prompt_fn:
                    current_prompt = improve_prompt_fn(task_query, issues)
                else:
                    current_prompt = f"{task_query}\n\n[REFLECTION FEEDBACK - FIX ISSUES]:\n" + "\n".join([f"- {iss}" for iss in issues])
                
                logger.info(f"[ReflectionEngine] Reflection feedback created: {feedback[:120]}")

        # Step 4: Compare & Publish best result
        final_result = best_candidate["execution_result"] if best_candidate else exec_result
        final_result["reflection_metadata"] = {
            "total_iterations": len(iterations_history),
            "best_score": best_score,
            "published_iteration": best_candidate["iteration"] if best_candidate else len(iterations_history),
            "history": [
                {"iteration": record["iteration"], "score": record["score"], "issues_count": len(record["issues"])}
                for record in iterations_history
            ]
        }
        return final_result

    def _diagnose_failures(self, issues: List[str], audit: Dict[str, Any]) -> str:
        """Diagnose root cause of failure across Verification Pyramid layers."""
        layers = audit.get("layers", {})
        failed_layers = []
        for lname, ldata in layers.items():
            if not ldata.get("passed"):
                failed_layers.append(lname)
        
        return f"Failed Pyramid Layers: {failed_layers}. Issues: {'; '.join(issues)}"
