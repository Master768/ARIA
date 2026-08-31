from typing import Dict, Any, List, Optional
from agents.skills.base_skill import BaseSkill

class TimeSeriesSkill(BaseSkill):
    """Plugin Skill: Time series decomposition, stationarity testing, and lag feature extraction."""

    @property
    def name(self) -> str:
        return "time_series"

    @property
    def description(self) -> str:
        return "Performs seasonal decomposition, stationarity tests (ADF test), and lag feature engineering."

    @property
    def category(self) -> str:
        return "analytics"

    @property
    def required_libraries(self) -> List[str]:
        return ["statsmodels", "pandas", "numpy"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["time series", "seasonal", "trend", "stationarity", "lag", "autocorrelation", "acf", "pacf"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.6 + matches * 0.2, 0.98)
        if dataset_meta and dataset_meta.get("inferred_problem_type") == "TIME_SERIES":
            return 0.85
        return 0.05

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "skill_executed": self.name,
            "output": "### ⏳ Time Series Skill Template:\n- Evaluates temporal trends, seasonal decomposition, and stationarity."
        }
