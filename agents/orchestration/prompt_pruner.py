import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("prompt_pruner")

class PromptPruner:
    @staticmethod
    def prune_for_visualization(query: str, dataset_profile: Dict[str, Any]) -> str:
        num_cols = dataset_profile.get("numeric_columns", [])[:5]
        cat_cols = dataset_profile.get("categorical_columns", [])[:5]

        pruned = f"""Target Query: {query}
Available Columns:
- Numeric: {', '.join(num_cols)}
- Categorical: {', '.join(cat_cols)}
Instruction: Generate a single clean Matplotlib/Seaborn plot script. Save plot image to a file and print PLOT_SAVED:<path>."""
        return pruned.strip()

    @staticmethod
    def prune_for_report(query: str, execution_output: str, stats_summary: Dict[str, Any]) -> str:
        truncated_out = execution_output[:1500] if execution_output else "No execution output."
        pruned = f"""User Question: {query}
Calculated Metrics: {stats_summary}
Sandbox Output Summary:
{truncated_out}
Instruction: Compile a clean markdown report with summary headers, bullet points, and key insights."""
        return pruned.strip()
