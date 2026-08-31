import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("pre_planner")

class RuleBasedPrePlanner:
    PATTERNS = {
        "DETERMINISTIC_INSPECT": [r"\b(inspect|shape|nulls|missing|columns|dtypes|data types)\b"],
        "DETERMINISTIC_STATS": [r"\b(summary stats|describe|mean|median|std|statistics|quantiles)\b"],
        "DETERMINISTIC_CORRELATION": [r"\b(correlation|corr matrix|pearson)\b"],
        "TOP_N_QUERY": [r"\b(top \d+|highest|best|lowest|bottom \d+)\b"],
        "VISUALIZATION_ONLY": [r"\b(plot|chart|graph|histogram|bar chart|scatter|distribution)\b"]
    }

    @classmethod
    def match_intent(cls, user_query: str) -> Optional[str]:
        q_lower = user_query.lower()
        for intent, patterns in cls.PATTERNS.items():
            for p in patterns:
                if re.search(p, q_lower):
                    return intent
        return None

    @classmethod
    def create_fast_dag(cls, user_query: str, main_dataset: str) -> Optional[Dict[str, Any]]:
        # Complex multi-step analytical queries must use full LLM planning & execution
        q_lower = user_query.lower()
        complex_indicators = [
            "explain", "why", "how", "compare", "identify", "overperformance",
            "feature importance", "despite", "contribute", "metric", "relationship",
            "predict", "model", "versus", "vs", "difference"
        ]
        if len(user_query.split()) > 10 or any(ind in q_lower for ind in complex_indicators):
            logger.info("[RuleBasedPrePlanner] Query is complex — routing to full LLM Planning Engine")
            return None

        intent = cls.match_intent(user_query)
        if not intent:
            return None

        if intent in ["DETERMINISTIC_INSPECT", "DETERMINISTIC_STATS"]:
            return {
                "manifest_id": "fast_manifest_stats",
                "intent": intent,
                "strategy": "Deterministic execution via Pandas engine without LLM code generation",
                "main_dataset": main_dataset,
                "fast_path": True,
                "nodes": [
                    {
                        "id": "node_eda_inspect",
                        "name": "Deterministic Inspection & Statistics",
                        "agent": "deterministic_engine",
                        "operations": ["inspect", "statistics"],
                        "depends_on": []
                    },
                    {
                        "id": "node_report",
                        "name": "Fast Report Compilation",
                        "agent": "report_writer",
                        "depends_on": ["node_eda_inspect"]
                    }
                ]
            }

        elif intent == "DETERMINISTIC_CORRELATION":
            return {
                "manifest_id": "fast_manifest_corr",
                "intent": intent,
                "strategy": "Deterministic Pearson Correlation matrix computation",
                "main_dataset": main_dataset,
                "fast_path": True,
                "nodes": [
                    {
                        "id": "node_corr",
                        "name": "Correlation Matrix Computation",
                        "agent": "deterministic_engine",
                        "operations": ["correlation"],
                        "depends_on": []
                    },
                    {
                        "id": "node_report",
                        "name": "Fast Correlation Report",
                        "agent": "report_writer",
                        "depends_on": ["node_corr"]
                    }
                ]
            }

        elif intent in ["TOP_N_QUERY", "VISUALIZATION_ONLY"]:
            return {
                "manifest_id": "fast_manifest_parallel",
                "intent": intent,
                "strategy": "Concurrent Parallel Data Analysis & Chart Generation DAG",
                "main_dataset": main_dataset,
                "fast_path": True,
                "nodes": [
                    {
                        "id": "node_preprocess",
                        "name": "Data Cleaning & Preparation",
                        "agent": "preprocessing_agent",
                        "depends_on": []
                    },
                    {
                        "id": "node_statistics",
                        "name": "Statistical Computations",
                        "agent": "data_agent",
                        "depends_on": ["node_preprocess"]
                    },
                    {
                        "id": "node_visualization",
                        "name": "Plot & Visualization Generation",
                        "agent": "data_agent",
                        "depends_on": ["node_preprocess"]
                    },
                    {
                        "id": "node_report",
                        "name": "Final Report Compilation",
                        "agent": "report_writer",
                        "depends_on": ["node_statistics", "node_visualization"]
                    }
                ]
            }

        return None
