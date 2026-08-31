import os
import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger("dataset_profile_store")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class DatasetProfileStore:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = os.path.abspath(cache_dir)
        else:
            self.cache_dir = os.path.join(PROJECT_ROOT, "config", "dataset_profiles")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _compute_sha256(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_or_create_profile(self, csv_path: str) -> Dict[str, Any]:
        if not os.path.exists(csv_path):
            return {}

        file_hash = self._compute_sha256(csv_path)
        cache_file = os.path.join(self.cache_dir, f"{file_hash}.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        try:
            df = pd.read_csv(csv_path)
            num_rows, num_cols = df.shape
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

            dtypes = {col: str(df[col].dtype) for col in df.columns}
            null_counts = {col: int(df[col].isnull().sum()) for col in df.columns}

            summary_stats = {}
            if numeric_cols:
                stats_df = df[numeric_cols].describe().T
                for col in numeric_cols:
                    summary_stats[col] = {
                        "mean": float(stats_df.loc[col, "mean"]) if col in stats_df.index else None,
                        "std": float(stats_df.loc[col, "std"]) if col in stats_df.index else None,
                        "min": float(stats_df.loc[col, "min"]) if col in stats_df.index else None,
                        "50%": float(stats_df.loc[col, "50%"]) if col in stats_df.index else None,
                        "max": float(stats_df.loc[col, "max"]) if col in stats_df.index else None,
                    }

            try:
                from agents.deterministic.dataset_intelligence_engine import DatasetIntelligenceEngine
                intelligence = DatasetIntelligenceEngine.analyze_dataset_intelligence(df)
            except Exception as ie:
                logger.warning(f"DatasetIntelligenceEngine profiling warning: {ie}")
                intelligence = {}

            profile = {
                "filepath": csv_path,
                "filename": os.path.basename(csv_path),
                "sha256": file_hash,
                "shape": [num_rows, num_cols],
                "columns": df.columns.tolist(),
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols,
                "dtypes": dtypes,
                "null_counts": null_counts,
                "summary_stats": summary_stats,
                "dataset_intelligence": intelligence
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
            return profile

        except Exception as e:
            logger.error(f"[DatasetProfileStore] Failed to profile CSV {csv_path}: {e}")
            return {}
