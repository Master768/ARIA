from typing import Dict, Any, List, Optional
from agents.skills.base_skill import BaseSkill

class VisualizationSkill(BaseSkill):
    """Plugin Skill: Seaborn/Matplotlib chart generation and visual plotting."""

    @property
    def name(self) -> str:
        return "visualization"

    @property
    def description(self) -> str:
        return "Generates plots, charts, distribution histograms, scatter matrices, and heatmaps using Seaborn and Matplotlib."

    @property
    def category(self) -> str:
        return "graphics"

    @property
    def required_libraries(self) -> List[str]:
        return ["matplotlib", "seaborn"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["plot", "chart", "visualize", "histogram", "heatmap", "distribution", "graph", "figure"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.5 + matches * 0.2, 0.95)
        return 0.1

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "skill_executed": self.name,
            "output": "### 🎨 Visualization Skill Template:\n- Generates Seaborn distribution plots, correlation heatmaps, and boxplots.\n- Recommendation: Limit correlation matrices to top 10 numeric columns (`df.select_dtypes(include=['number']).columns[:10]`) for instant rendering."
        }
