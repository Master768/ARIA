import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger("deterministic_engine")

class DeterministicComputeEngine:
    """Tier 6 Zero-LLM Deterministic Intelligence."""

    @staticmethod
    def inspect_dataset(df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "total_nulls": int(df.isnull().sum().sum())
        }

    @staticmethod
    def compute_summary_statistics(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        target_df = df[columns] if columns else df.select_dtypes(include=[np.number])
        if target_df.empty:
            return {}

        desc = target_df.describe().T
        result = {}
        for col in target_df.columns:
            if col in desc.index:
                result[col] = {
                    "count": int(desc.loc[col, "count"]),
                    "mean": float(desc.loc[col, "mean"]),
                    "std": float(desc.loc[col, "std"]),
                    "min": float(desc.loc[col, "min"]),
                    "25%": float(desc.loc[col, "25%"]),
                    "50%": float(desc.loc[col, "50%"]),
                    "75%": float(desc.loc[col, "75%"]),
                    "max": float(desc.loc[col, "max"]),
                    "skew": float(target_df[col].skew()) if len(target_df[col].dropna()) > 2 else 0.0
                }
        return result

    @staticmethod
    def compute_correlation_matrix(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        num_df = df[columns] if columns else df.select_dtypes(include=[np.number])
        if num_df.empty or len(num_df.columns) < 2:
            return {}
        return num_df.corr().round(4).to_dict()

    @staticmethod
    def get_top_n(df: pd.DataFrame, group_col: str, value_col: str, n: int = 10, ascending: bool = False) -> Dict[str, Any]:
        if group_col not in df.columns or value_col not in df.columns:
            return {}
        grouped = df.groupby(group_col)[value_col].sum().reset_index()
        top_n = grouped.sort_values(by=value_col, ascending=ascending).head(n)
        return {"group_col": group_col, "value_col": value_col, "top_records": top_n.to_dict(orient="records")}

    @staticmethod
    def execute_deterministic_pipeline(csv_path: str, operations: List[str]) -> Dict[str, Any]:
        if not csv_path or not os.path.exists(csv_path):
            return {"error": "Invalid CSV path"}
        df = pd.read_csv(csv_path)
        results = {}
        for op in operations:
            if op == "inspect":
                results["inspection"] = DeterministicComputeEngine.inspect_dataset(df)
            elif op == "statistics":
                results["statistics"] = DeterministicComputeEngine.compute_summary_statistics(df)
            elif op == "correlation":
                results["correlation"] = DeterministicComputeEngine.compute_correlation_matrix(df)
        return results
