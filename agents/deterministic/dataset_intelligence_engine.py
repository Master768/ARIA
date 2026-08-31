import os
import re
import math
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("dataset_intelligence_engine")

class SemanticTypeDetector:
    """Detects universal semantic types for DataFrame columns."""

    PATTERNS = {
        "ID": [r"\b(id|uuid|guid|pk|index|key|number|code)\b"],
        "CURRENCY": [r"\b(salary|price|cost|revenue|income|fee|amount|val|budget|wage|pay|tax|spend)\b"],
        "CHURN_TARGET": [r"\b(churn|attrition|exited|left|cancelled|churned)\b"],
        "BINARY_TARGET": [r"\b(target|label|status|default|fraud|converted|passed|approved|outcome|success|is_)\b"],
        "RATING_TARGET": [r"\b(rating|score|rank|performance|grade)\b"],
        "DATETIME": [r"\b(date|time|timestamp|created_at|updated_at|year|month|day)\b"]
    }

    @classmethod
    def detect_column_semantic_type(cls, col_name: str, series: pd.Series) -> str:
        col_lower = col_name.lower().strip()
        col_clean = col_lower.replace("_", " ").replace("-", " ")
        num_unique = series.nunique(dropna=True)
        total_count = len(series)

        # 1. Unique Key / ID
        if num_unique == total_count and total_count > 10:
            if series.dtype == "object" or any(re.search(p, col_clean) for p in cls.PATTERNS["ID"]):
                return "UNIQUE_ID"

        # 2. Datetime / Temporal
        if pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"
        if any(re.search(p, col_clean) for p in cls.PATTERNS["DATETIME"]):
            return "DATETIME"

        # 3. Categorical Binary
        if num_unique == 2:
            return "CATEGORICAL_BINARY"

        # 4. Currency / Financial Numeric
        if any(re.search(p, col_clean) for p in cls.PATTERNS["CURRENCY"]):
            return "CURRENCY_NUMERIC"

        # 5. Categorical Multiclass
        if series.dtype == "object" or isinstance(series.dtype, pd.CategoricalDtype):
            return "CATEGORICAL_MULTICLASS" if num_unique < 50 else "TEXT_HIGH_CARDINALITY"

        # 6. Continuous Numeric
        if pd.api.types.is_numeric_dtype(series):
            if num_unique < 15:
                return "CATEGORICAL_NUMERIC_DISCRETE"
            return "CONTINUOUS_NUMERIC"

        return "UNKNOWN"


class BusinessMeaningInferencer:
    """Infers business meaning and domain concepts."""

    DOMAIN_MAPPINGS = {
        "COMPENSATION_FINANCIAL": [r"\b(salary|wage|pay|income|revenue|price|cost|budget)\b"],
        "RETENTION_CHURN": [r"\b(churn|attrition|exited|renewal|retention)\b"],
        "CUSTOMER_DEMOGRAPHIC": [r"\b(age|gender|country|city|state|zip|education)\b"],
        "TEMPORAL_ACTIVITY": [r"\b(date|timestamp|year|month|tenure|duration|minutes)\b"],
        "PERFORMANCE_RATING": [r"\b(rating|score|performance|grade|rank|efficiency)\b"]
    }

    @classmethod
    def infer_business_meaning(cls, col_name: str, semantic_type: str) -> str:
        col_lower = col_name.lower().strip()
        col_clean = col_lower.replace("_", " ").replace("-", " ")
        for domain, patterns in cls.DOMAIN_MAPPINGS.items():
            for p in patterns:
                if re.search(p, col_clean):
                    return domain

        if semantic_type == "CURRENCY_NUMERIC":
            return "COMPENSATION_FINANCIAL"
        elif semantic_type == "DATETIME":
            return "TEMPORAL_ACTIVITY"
        elif semantic_type in ["CATEGORICAL_BINARY", "CATEGORICAL_MULTICLASS"]:
            return "CATEGORICAL_ATTRIBUTE"
        return "GENERAL_FEATURE"


class TargetDetector:
    """Automatically detects candidate target variable and problem type."""

    @classmethod
    def detect_target_and_problem(cls, df: pd.DataFrame, user_query: str = "") -> Dict[str, Any]:
        q_lower = user_query.lower()
        columns = df.columns.tolist()

        # Step 1: Query-driven target detection if specified
        for col in columns:
            if col.lower() in q_lower and len(col) > 2:
                s = df[col]
                sem_type = SemanticTypeDetector.detect_column_semantic_type(col, s)
                problem_type = cls._infer_problem_type(s, sem_type)
                return {
                    "target_column": col,
                    "problem_type": problem_type,
                    "confidence": 0.98,
                    "detection_method": "QUERY_MATCH"
                }

        # Step 2: Pattern-driven target detection
        candidate_scores: List[Tuple[str, float, str]] = []

        for col in columns:
            col_lower = col.lower().strip()
            col_clean = col_lower.replace("_", " ").replace("-", " ")
            s = df[col]
            num_unique = s.nunique(dropna=True)
            sem_type = SemanticTypeDetector.detect_column_semantic_type(col, s)

            # High priority targets
            if re.search(r"\b(churn|attrition|exited|default|fraud|converted|target|label|outcome)\b", col_clean):
                candidate_scores.append((col, 0.95, cls._infer_problem_type(s, sem_type)))
            elif re.search(r"\b(salary|price|revenue|cost|income|rating|performance score|tournament rating)\b", col_clean):
                candidate_scores.append((col, 0.90, cls._infer_problem_type(s, sem_type)))
            elif sem_type == "CATEGORICAL_BINARY" and not col_lower.startswith("is_"):
                candidate_scores.append((col, 0.70, "CLASSIFICATION"))

        if candidate_scores:
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            top_target, conf, prob_type = candidate_scores[0]
            return {
                "target_column": top_target,
                "problem_type": prob_type,
                "confidence": conf,
                "detection_method": "SEMANTIC_PATTERN"
            }

        # Step 3: Fallback — select last non-ID column
        for col in reversed(columns):
            sem_type = SemanticTypeDetector.detect_column_semantic_type(col, df[col])
            if sem_type != "UNIQUE_ID":
                prob_type = cls._infer_problem_type(df[col], sem_type)
                return {
                    "target_column": col,
                    "problem_type": prob_type,
                    "confidence": 0.50,
                    "detection_method": "FALLBACK_POSITION"
                }

        return {
            "target_column": columns[-1] if columns else None,
            "problem_type": "EDA_EXPLORATORY",
            "confidence": 0.30,
            "detection_method": "DEFAULT"
        }

    @staticmethod
    def _infer_problem_type(series: pd.Series, sem_type: str) -> str:
        if pd.api.types.is_datetime64_any_dtype(series) or sem_type == "DATETIME":
            return "TIME_SERIES"
        if sem_type in ["CURRENCY_NUMERIC"]:
            return "REGRESSION"
        if series.nunique(dropna=True) == 2 or sem_type in ["CATEGORICAL_BINARY", "CHURN_TARGET"]:
            return "CLASSIFICATION"
        if pd.api.types.is_float_dtype(series):
            return "REGRESSION"
        if pd.api.types.is_numeric_dtype(series):
            if series.nunique(dropna=True) > 10 or series.nunique(dropna=True) == len(series):
                return "REGRESSION"
            return "CLASSIFICATION"
        if series.nunique(dropna=True) < 20:
            return "CLASSIFICATION"
        return "REGRESSION"


class DatasetIntelligenceEngine:
    """
    Tier 6 Zero-LLM Dataset Intelligence Engine.
    Executes full semantic type, target, relationship, and feature importance analysis (< 100ms).
    """

    @classmethod
    def analyze_dataset_intelligence(cls, df: pd.DataFrame, user_query: str = "") -> Dict[str, Any]:
        if df.empty:
            return {}

        # 1. Column Semantic Types & Business Meaning
        columns_meta = {}
        for col in df.columns:
            series = df[col]
            sem_type = SemanticTypeDetector.detect_column_semantic_type(col, series)
            biz_meaning = BusinessMeaningInferencer.infer_business_meaning(col, sem_type)
            columns_meta[col] = {
                "dtype": str(series.dtype),
                "semantic_type": sem_type,
                "business_meaning": biz_meaning,
                "null_pct": round(float(series.isnull().mean() * 100), 2),
                "unique_count": int(series.nunique(dropna=True))
            }

        # 2. Target & Problem Type Detection
        target_info = TargetDetector.detect_target_and_problem(df, user_query)
        target_col = target_info.get("target_column")
        problem_type = target_info.get("problem_type", "EDA_EXPLORATORY")

        # 3. Feature Importance & Relationships
        feature_importances = cls._compute_feature_importance(df, target_col, problem_type)
        top_correlations = cls._compute_top_correlations(df, target_col)

        # 4. Suggested Analytical Pipelines
        suggested_pipelines = cls._generate_suggested_pipelines(problem_type, target_col, feature_importances)

        return {
            "columns_meta": columns_meta,
            "target_detection": target_info,
            "inferred_problem_type": problem_type,
            "feature_importance": feature_importances,
            "top_correlations": top_correlations,
            "suggested_pipelines": suggested_pipelines
        }

    @classmethod
    def _compute_feature_importance(cls, df: pd.DataFrame, target_col: Optional[str], problem_type: str) -> Dict[str, float]:
        if not target_col or target_col not in df.columns:
            return {}

        try:
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            from sklearn.preprocessing import LabelEncoder

            clean_df = df.dropna(subset=[target_col]).copy()
            if len(clean_df) < 10:
                return {}

            X = clean_df.drop(columns=[target_col])
            y = clean_df[target_col]

            numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return {}

            X_num = X[numeric_cols].fillna(X[numeric_cols].median())

            if problem_type == "CLASSIFICATION":
                le = LabelEncoder()
                y_enc = le.fit_transform(y.astype(str))
                model = RandomForestClassifier(n_estimators=30, max_depth=5, random_state=42)
                model.fit(X_num, y_enc)
            elif problem_type == "REGRESSION":
                y_num = pd.to_numeric(y, errors="coerce").fillna(0)
                model = RandomForestRegressor(n_estimators=30, max_depth=5, random_state=42)
                model.fit(X_num, y_num)
            else:
                return {}

            importances = dict(zip(numeric_cols, [round(float(v), 4) for v in model.feature_importances_]))
            sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True)[:10])
            return sorted_imp

        except Exception as e:
            logger.warning(f"Feature importance calculation skipped: {e}")
            return {}

    @classmethod
    def _compute_top_correlations(cls, df: pd.DataFrame, target_col: Optional[str]) -> List[Dict[str, Any]]:
        if not target_col or target_col not in df.columns:
            return []
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            if target_col not in numeric_df.columns or len(numeric_df.columns) < 2:
                return []
            corr = numeric_df.corr()[target_col].drop(target_col, errors="ignore").dropna()
            abs_corr = corr.abs().sort_values(ascending=False).head(5)
            results = []
            for col in abs_corr.index:
                results.append({
                    "column": col,
                    "correlation": round(float(corr[col]), 4)
                })
            return results
        except Exception:
            return []

    @classmethod
    def _generate_suggested_pipelines(cls, problem_type: str, target_col: Optional[str], feature_imp: Dict[str, float]) -> List[str]:
        pipelines = []
        top_feats = list(feature_imp.keys())[:3]
        feats_str = ", ".join(top_feats) if top_feats else "numeric features"

        if problem_type == "CLASSIFICATION":
            pipelines.append(f"🎯 Binary/Multiclass Classification for '{target_col}' using Logistic Regression & Random Forest")
            pipelines.append(f"🔍 Key Predictor Evaluation: Analyze drivers ({feats_str}) relative to '{target_col}'")
            pipelines.append(f"📊 Confusion Matrix, ROC-AUC Curve, and Stratified Cross-Validation")
        elif problem_type == "REGRESSION":
            pipelines.append(f"📈 Linear & Gradient Boosting Regression modeling to forecast '{target_col}'")
            pipelines.append(f"🔍 Feature Impact Analysis: Top variance drivers ({feats_str})")
            pipelines.append(f"📊 Residual Plot & RMSE/R² Accuracy Assessment")
        elif problem_type == "TIME_SERIES":
            pipelines.append(f"⏳ Temporal Trend Analysis & Time-Series Decomposition on '{target_col}'")
            pipelines.append(f"📊 Seasonality & Lagged Moving Average forecasting")
        else:
            pipelines.append(f"📊 Exploratory Data Analysis & Summary Metric Aggregation")

        return pipelines
