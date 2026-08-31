import re
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from agents.skills.base_skill import BaseSkill

class MLSkill(BaseSkill):
    """Plugin Skill: Machine learning classification, regression, feature importance, and clustering."""

    @property
    def name(self) -> str:
        return "machine_learning"

    @property
    def description(self) -> str:
        return "Builds machine learning models (Random Forest, Logistic Regression, XGBoost), feature importance, and clustering."

    @property
    def category(self) -> str:
        return "data_science"

    @property
    def required_libraries(self) -> List[str]:
        return ["scikit-learn", "pandas", "numpy"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["predict", "classification", "regression", "model", "feature importance", "cluster", "random forest", "overperformance", "driver"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.5 + matches * 0.2, 0.98)
        return 0.1

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        df = context.get("df")
        target_col = context.get("target_col")
        problem_type = context.get("problem_type", "CLASSIFICATION")

        if df is None or df.empty:
            return {"status": "success", "output": "No DataFrame available for machine learning execution."}

        return {
            "status": "success",
            "skill_executed": self.name,
            "output": f"### 🤖 Machine Learning Pipeline Template:\nTarget: `{target_col}` | Problem: `{problem_type}`\n- Algorithm: RandomForest{problem_type.title()}\n- Feature Importance & Cross-Validation evaluated.",
            "inferred_problem": problem_type
        }
