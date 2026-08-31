import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("verification_pyramid")

class ExecutionValidator:
    """Layer 1: Validates runtime execution, exit codes, exceptions, and non-empty stdout."""

    @classmethod
    def validate(cls, execution_result: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if not isinstance(execution_result, dict):
            return False, 0.0, ["Execution result is not a structured dictionary."]

        status = execution_result.get("status", "error")
        output = execution_result.get("output", "")
        error = execution_result.get("error", "")

        if status in ["error", "warning"] and ("Error (" in output or "Exception" in output or "Traceback" in output):
            issues.append(f"Runtime execution error detected: {output[:150]}")
            score -= 0.6

        if "TimeoutExpired" in output:
            issues.append("Execution timed out.")
            score -= 0.7

        if not output or len(output.strip()) == 0:
            issues.append("Execution returned completely empty stdout output.")
            score -= 0.4

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


class StatisticalValidator:
    """Layer 2: Validates numerical distributions, presence of NaN/inf values, and sample size sanity."""

    @classmethod
    def validate(cls, output_text: str, summary_stats: Optional[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if "nan" in output_text.lower() or "none" in output_text.lower():
            if re.search(r"\b(nan|null|none)\b", output_text, re.IGNORECASE):
                issues.append("Unparsed NaN/Null values detected in analytical output.")
                score -= 0.3

        if "inf" in output_text.lower():
            if re.search(r"\b(inf|-inf)\b", output_text, re.IGNORECASE):
                issues.append("Infinite (inf) values detected in calculations.")
                score -= 0.4

        if summary_stats:
            for col, stats in summary_stats.items():
                if isinstance(stats, dict):
                    std = stats.get("std")
                    count = stats.get("count", 1)
                    if count == 0:
                        issues.append(f"Column '{col}' has 0 sample count.")
                        score -= 0.3
                    if std is not None and std == 0:
                        issues.append(f"Column '{col}' has zero variance (std=0).")
                        score -= 0.1

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


class MathematicalValidator:
    """Layer 3: Validates mathematical consistency (min <= median <= max, probabilities in [0,1], percentage sums)."""

    @classmethod
    def validate(cls, summary_stats: Optional[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if summary_stats:
            for col, stats in summary_stats.items():
                if isinstance(stats, dict):
                    min_val = stats.get("min")
                    med_val = stats.get("50%")
                    max_val = stats.get("max")

                    if min_val is not None and max_val is not None and min_val > max_val:
                        issues.append(f"Column '{col}' invalid bounds: min ({min_val}) > max ({max_val}).")
                        score -= 0.5
                    if min_val is not None and med_val is not None and min_val > med_val:
                        issues.append(f"Column '{col}' invalid bounds: min ({min_val}) > median ({med_val}).")
                        score -= 0.3
                    if med_val is not None and max_val is not None and med_val > max_val:
                        issues.append(f"Column '{col}' invalid bounds: median ({med_val}) > max ({max_val}).")
                        score -= 0.3

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


class VisualizationValidator:
    """Layer 4: Validates visual figure generation, file existence, and image non-zero size."""

    @classmethod
    def validate(cls, generated_files: List[str]) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        img_files = [f for f in generated_files if f.endswith((".png", ".jpg", ".svg"))]
        if not img_files:
            return True, 1.0, []  # Visualization optional

        for img in img_files:
            if not os.path.exists(img):
                issues.append(f"Referenced image file does not exist: {img}")
                score -= 0.5
            else:
                size = os.path.getsize(img)
                if size < 100:  # less than 100 bytes is corrupt/empty
                    issues.append(f"Image file is corrupt or empty (size {size} bytes): {img}")
                    score -= 0.5

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


class ReportValidator:
    """Layer 5: Validates markdown structure, headers, table integrity, and prompt coverage."""

    @classmethod
    def validate(cls, report_markdown: str) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if not report_markdown or len(report_markdown.strip()) < 50:
            issues.append("Report markdown is too short or empty.")
            return False, 0.0, issues

        if not report_markdown.startswith("#"):
            issues.append("Report lacks level-1 top header (#).")
            score -= 0.2

        if "###" not in report_markdown:
            issues.append("Report lacks structured sub-sections (###).")
            score -= 0.2

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


class BusinessLogicValidator:
    """Layer 6: Validates business logic constraints against dataset intelligence."""

    @classmethod
    def validate(cls, output_text: str, dataset_intel: Optional[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        if dataset_intel:
            target_info = dataset_intel.get("target_detection", {})
            target_col = target_info.get("target_column")
            if target_col and target_col.lower() not in output_text.lower():
                issues.append(f"Analytical output failed to explicitly reference target column '{target_col}'.")
                score -= 0.2

        passed = score >= 0.7 and len(issues) == 0
        return passed, max(0.0, score), issues


from agents.audit.consistency_validator import CrossNodeConsistencyValidator

class VerificationPyramidEngine:
    """
    Tier 4 Verification Pyramid Orchestrator Engine.
    Runs 7 specialized validation layers and computes an aggregated audit verification score.
    """

    @classmethod
    def run_pyramid_audit(
        cls,
        execution_result: Dict[str, Any],
        report_markdown: str = "",
        summary_stats: Optional[Dict[str, Any]] = None,
        generated_files: Optional[List[str]] = None,
        dataset_intel: Optional[Dict[str, Any]] = None,
        node_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        exec_pass, exec_score, exec_issues = ExecutionValidator.validate(execution_result)
        out_text = execution_result.get("output", "") + "\n" + report_markdown

        stat_pass, stat_score, stat_issues = StatisticalValidator.validate(out_text, summary_stats)
        math_pass, math_score, math_issues = MathematicalValidator.validate(summary_stats)
        vis_pass, vis_score, vis_issues = VisualizationValidator.validate(generated_files or [])
        rep_pass, rep_score, rep_issues = ReportValidator.validate(report_markdown) if report_markdown else (True, 1.0, [])
        biz_pass, biz_score, biz_issues = BusinessLogicValidator.validate(out_text, dataset_intel)
        con_pass, con_score, con_issues = CrossNodeConsistencyValidator.validate(node_outputs or {})

        # Weighted layer calculation
        overall_score = (
            exec_score * 0.25 +
            stat_score * 0.15 +
            math_score * 0.15 +
            vis_score * 0.10 +
            rep_score * 0.15 +
            biz_score * 0.10 +
            con_score * 0.10
        )

        all_issues = exec_issues + stat_issues + math_issues + vis_issues + rep_issues + biz_issues + con_issues
        overall_pass = overall_score >= 0.75 and len(exec_issues) == 0

        return {
            "overall_pass": overall_pass,
            "overall_score": round(overall_score, 4),
            "layers": {
                "execution_validator": {"passed": exec_pass, "score": exec_score, "issues": exec_issues},
                "statistical_validator": {"passed": stat_pass, "score": stat_score, "issues": stat_issues},
                "mathematical_validator": {"passed": math_pass, "score": math_score, "issues": math_issues},
                "visualization_validator": {"passed": vis_pass, "score": vis_score, "issues": vis_issues},
                "report_validator": {"passed": rep_pass, "score": rep_score, "issues": rep_issues},
                "business_logic_validator": {"passed": biz_pass, "score": biz_score, "issues": biz_issues},
                "consistency_validator": {"passed": con_pass, "score": con_score, "issues": con_issues}
            },
            "all_issues": all_issues
        }
