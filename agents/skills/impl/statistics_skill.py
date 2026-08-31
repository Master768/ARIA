import re
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from agents.skills.base_skill import BaseSkill

class StatisticsSkill(BaseSkill):
    """Plugin Skill: Descriptive statistics, summary metrics, hypothesis testing, and correlations."""

    @property
    def name(self) -> str:
        return "statistics"

    @property
    def description(self) -> str:
        return "Computes summary statistics, distributions, percentiles, correlation matrices, and t-tests."

    @property
    def category(self) -> str:
        return "analytics"

    @property
    def required_libraries(self) -> List[str]:
        return ["pandas", "numpy", "scipy"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["statistic", "summary", "mean", "median", "correlation", "variance", "std", "percentile", "ttest", "anova"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.4 + matches * 0.2, 0.95)
        return 0.2

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        df = context.get("df")
        if df is None or df.empty:
            return {"status": "success", "output": "No active DataFrame provided for statistical analysis."}

        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {"status": "success", "output": "No numeric columns found for statistical summary."}

        desc = numeric_df.describe().T
        summary_lines = []
        for col in desc.index[:10]:
            summary_lines.append(
                f"- **{col}**: count={desc.loc[col, 'count']:.0f}, mean={desc.loc[col, 'mean']:.2f}, "
                f"std={desc.loc[col, 'std']:.2f}, median={desc.loc[col, '50%']:.2f}, max={desc.loc[col, 'max']:.2f}"
            )

        return {
            "status": "success",
            "skill_executed": self.name,
            "output": "### 📊 Statistical Summary Metrics:\n" + "\n".join(summary_lines),
            "summary_dict": desc.to_dict()
        }
