from typing import Dict, Any, List, Optional
from agents.skills.base_skill import BaseSkill

class OptimizationSkill(BaseSkill):
    """Plugin Skill: Linear programming, SciPy optimize solvers, resource allocation, and constraint handling."""

    @property
    def name(self) -> str:
        return "optimization"

    @property
    def description(self) -> str:
        return "Solves linear programming, resource allocation, portfolio optimization, and constraint maximization problems using SciPy."

    @property
    def category(self) -> str:
        return "optimization"

    @property
    def required_libraries(self) -> List[str]:
        return ["scipy", "numpy"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["optimize", "maximize", "minimize", "linear programming", "constraint", "allocation", "solver"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.6 + matches * 0.2, 0.98)
        return 0.05

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "skill_executed": self.name,
            "output": "### ⚙️ Optimization Skill Template:\n- Solves objective function minimization/maximization under linear constraints."
        }
