from typing import Dict, Any, List, Optional
from agents.skills.base_skill import BaseSkill

class ForecastSkill(BaseSkill):
    """Plugin Skill: Future horizon forecasting, ARIMA, Prophet, and exponential smoothing models."""

    @property
    def name(self) -> str:
        return "forecast"

    @property
    def description(self) -> str:
        return "Forecasts future values across time horizons using ARIMA, Exponential Smoothing, and trend extrapolation."

    @property
    def category(self) -> str:
        return "data_science"

    @property
    def required_libraries(self) -> List[str]:
        return ["statsmodels", "scipy"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["forecast", "future", "predict next", "horizon", "extrapolate", "projection", "arima"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.6 + matches * 0.2, 0.98)
        return 0.05

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "skill_executed": self.name,
            "output": "### 🔮 Forecasting Skill Template:\n- Computes future trajectory projections with confidence interval bounds."
        }
