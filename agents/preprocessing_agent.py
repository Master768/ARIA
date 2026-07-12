import os
import logging
import json
from typing import Optional, Dict, List, Tuple
from datetime import datetime

import numpy as np
import pandas as pd
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class DataProfile(BaseModel):
    """Data profiling results."""
    shape: Tuple[int, int]          # (rows, cols)
    memory_mb: float
    dtypes_summary: Dict[str, int]
    missing_data: Dict[str, float]  # {col: null_pct}
    duplicates: int
    numeric_cols: List[str]
    categorical_cols: List[str]


class QualityMetrics(BaseModel):
    """Data quality assessment across five dimensions."""
    completeness: float             # % non-null values
    uniqueness: float               # avg % unique per column
    validity: float                 # % values in valid range
    consistency: float              # % consistent types
    accuracy: float                 # % no obvious errors
    overall_quality_score: float    # weighted 0-100


class EDASummary(BaseModel):
    """Complete EDA output package."""
    timestamp: str
    data_profile: DataProfile
    quality_metrics: QualityMetrics
    statistical_summary: Dict
    missing_data_analysis: Dict
    outliers_detected: Dict
    categorical_analysis: Dict
    correlation_analysis: Dict
    recommendations: List[str]
    cleaning_steps: List[str]
    is_ready_for_analysis: bool
    warnings: List[str]


# ---------------------------------------------------------------------------
# Main agent
# ---------------------------------------------------------------------------

class DataPreprocessingAgent:
    """
    Validates, profiles, cleans, and prepares data before any analysis begins.

    Usage::

        agent = DataPreprocessingAgent()
        summary = agent.preprocess_data("data/telco_churn.csv", task_id=1)
        agent.generate_eda_report(summary, "reports/eda_1.md")

        if summary.is_ready_for_analysis:
            print(f"✓ Quality: {summary.quality_metrics.overall_quality_score:.1f}/100")
        else:
            print("⚠ Data issues:", summary.warnings)
    """

    # Quality threshold: datasets scoring below this are flagged as not ready
    QUALITY_THRESHOLD = 75.0

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Optional LLM client (GroqOllamaClient or compatible).
                        Reserved for future LLM-driven insight generation.
        """
        self.llm = llm_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def preprocess_data(self, filepath: str, task_id: int = 0) -> EDASummary:
        """
        Main entry point: load data and perform complete EDA.

        Args:
            filepath: Path to CSV / Excel / JSON file.
            task_id:  Optional task identifier for log tracing.

        Returns:
            EDASummary with all EDA results, recommendations, and readiness flag.
        """
        logger.info(f"[PreprocessingAgent] Starting EDA for '{filepath}' (task_id={task_id})")

        df = self._load_data(filepath)
        logger.info(f"[PreprocessingAgent] Loaded: {df.shape[0]} rows × {df.shape[1]} cols")

        profile      = self._profile_data(df)
        quality      = self._assess_quality(df, profile)
        stats        = self._statistical_summary(df)
        missing      = self._analyze_missing_data(df)
        outliers     = self._detect_outliers(df)
        categorical  = self._analyze_categorical(df)
        correlations = self._analyze_correlations(df)

        recommendations = self._generate_recommendations(
            profile, quality, missing, outliers, categorical, correlations
        )
        cleaning_steps  = self._get_cleaning_steps(missing)
        warnings        = self._generate_warnings(profile, quality, missing, outliers)
        is_ready        = quality.overall_quality_score >= self.QUALITY_THRESHOLD

        summary = EDASummary(
            timestamp=datetime.now().isoformat(),
            data_profile=profile,
            quality_metrics=quality,
            statistical_summary=stats,
            missing_data_analysis=missing,
            outliers_detected=outliers,
            categorical_analysis=categorical,
            correlation_analysis=correlations,
            recommendations=recommendations,
            cleaning_steps=cleaning_steps,
            is_ready_for_analysis=is_ready,
            warnings=warnings,
        )

        logger.info(
            f"[PreprocessingAgent] EDA complete. "
            f"Quality={quality.overall_quality_score:.1f}/100 | Ready={is_ready}"
        )
        return summary

    def generate_eda_report(self, summary: EDASummary, output_path: str = "eda_report.md") -> str:
        """
        Write a formatted markdown EDA report to *output_path* and return the text.
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        quality_icon = "✅" if summary.is_ready_for_analysis else "❌"

        report = f"""# Exploratory Data Analysis Report
Generated: {summary.timestamp}

---

## 1. Data Profile

| Property | Value |
|---|---|
| **Shape** | {summary.data_profile.shape[0]:,} rows × {summary.data_profile.shape[1]} columns |
| **Memory** | {summary.data_profile.memory_mb:.2f} MB |
| **Duplicate rows** | {summary.data_profile.duplicates:,} |
| Numeric (int) | {summary.data_profile.dtypes_summary.get('numeric_int', 0)} |
| Numeric (float) | {summary.data_profile.dtypes_summary.get('numeric_float', 0)} |
| Categorical | {summary.data_profile.dtypes_summary.get('categorical', 0)} |
| Boolean | {summary.data_profile.dtypes_summary.get('boolean', 0)} |
| Datetime | {summary.data_profile.dtypes_summary.get('datetime', 0)} |

---

## 2. Data Quality Score  — {summary.quality_metrics.overall_quality_score:.1f} / 100

| Dimension | Score |
|---|---|
| Completeness | {summary.quality_metrics.completeness:.1f}% |
| Uniqueness | {summary.quality_metrics.uniqueness:.1f}% |
| Validity | {summary.quality_metrics.validity:.1f}% |
| Consistency | {summary.quality_metrics.consistency:.1f}% |
| Accuracy | {summary.quality_metrics.accuracy:.1f}% |

---

## 3. Missing Data Analysis

{self._format_missing_section(summary.missing_data_analysis)}

---

## 4. Statistical Summary

{self._format_stats_section(summary.statistical_summary)}

---

## 5. Outliers Detected (IQR Method)

{self._format_outliers_section(summary.outliers_detected)}

---

## 6. Categorical Analysis

{self._format_categorical_section(summary.categorical_analysis)}

---

## 7. Correlation Analysis

{self._format_correlation_section(summary.correlation_analysis)}

---

## 8. Recommendations

{chr(10).join(f'- {r}' for r in summary.recommendations) or 'None'}

---

## 9. Suggested Cleaning Steps

{chr(10).join(f'- {s}' for s in summary.cleaning_steps) or 'None'}

---

## 10. Data Readiness

**{quality_icon} Ready for Analysis: {'YES' if summary.is_ready_for_analysis else 'NO'}**

### Warnings

{chr(10).join(f'- {w}' for w in summary.warnings) if summary.warnings else 'None — data looks clean ✓'}
"""

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(report)

        logger.info(f"[PreprocessingAgent] EDA report saved → {output_path}")
        return report

    # ------------------------------------------------------------------
    # Private: data loading
    # ------------------------------------------------------------------

    def _load_data(self, filepath: str) -> pd.DataFrame:
        """Load CSV, Excel, or JSON into a DataFrame."""
        try:
            ext = os.path.splitext(filepath)[-1].lower()
            if ext == ".csv":
                df = pd.read_csv(filepath)
            elif ext in (".xls", ".xlsx"):
                df = pd.read_excel(filepath)
            elif ext == ".json":
                df = pd.read_json(filepath)
            else:
                # Fallback: try CSV
                df = pd.read_csv(filepath)
            logger.info(f"[PreprocessingAgent] Loaded {len(df):,} rows, {len(df.columns)} cols from '{filepath}'")
            return df
        except Exception as exc:
            logger.error(f"[PreprocessingAgent] Failed to load '{filepath}': {exc}")
            raise

    # ------------------------------------------------------------------
    # Private: profiling
    # ------------------------------------------------------------------

    def _profile_data(self, df: pd.DataFrame) -> DataProfile:
        """Return a DataProfile summarising shape, types, nulls, and duplicates."""
        dtypes = df.dtypes
        dtypes_summary = {
            "numeric_int":   int((dtypes == "int64").sum() + (dtypes == "int32").sum()),
            "numeric_float": int((dtypes == "float64").sum() + (dtypes == "float32").sum()),
            "categorical":   int((dtypes == "object").sum()),
            "boolean":       int((dtypes == "bool").sum()),
            "datetime":      int(dtypes.astype(str).str.contains("datetime").sum()),
        }

        numeric_cols     = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        missing_data = {
            k: float(round(v, 4))
            for k, v in (df.isnull().sum() / len(df) * 100).items()
            if v > 0
        }

        return DataProfile(
            shape=df.shape,
            memory_mb=round(df.memory_usage(deep=True).sum() / 1024 ** 2, 4),
            dtypes_summary=dtypes_summary,
            missing_data=missing_data,
            duplicates=int(df.duplicated().sum()),
            numeric_cols=numeric_cols,
            categorical_cols=categorical_cols,
        )

    # ------------------------------------------------------------------
    # Private: quality assessment
    # ------------------------------------------------------------------

    def _assess_quality(self, df: pd.DataFrame, profile: DataProfile) -> QualityMetrics:
        """Score data quality on five weighted dimensions (0-100 each)."""
        total_values = df.shape[0] * df.shape[1]

        # Completeness: fraction of non-null cells
        completeness = float((1 - df.isnull().sum().sum() / max(total_values, 1)) * 100)

        # Uniqueness: average unique-value ratio per column (capped at 100)
        uniqueness = float(min(df.nunique(dropna=False).mean() / max(len(df), 1) * 100, 100))

        # Validity: penalise every numeric column whose range includes impossible negatives
        #           (simple heuristic — can be extended with domain rules)
        n_numeric = len(profile.numeric_cols)
        if n_numeric:
            invalid_cols = sum(
                1 for c in profile.numeric_cols
                if df[c].min() < 0 and c.lower() in ("age", "tenure", "quantity", "count")
            )
            validity = float(max(0, 100 - (invalid_cols / n_numeric) * 100))
        else:
            validity = 95.0

        # Consistency: penalise columns that appear numeric but are stored as object
        n_obj = len(profile.categorical_cols)
        numeric_stored_as_obj = 0
        for col in profile.categorical_cols:
            try:
                pd.to_numeric(df[col].dropna(), errors="raise")
                numeric_stored_as_obj += 1
            except (ValueError, TypeError):
                pass
        consistency = float(max(0, 100 - (numeric_stored_as_obj / max(n_obj, 1)) * 100))

        # Accuracy: penalise duplicate rows and high-missing columns
        dup_penalty  = min(profile.duplicates / max(len(df), 1) * 100, 20)
        high_missing = sum(1 for v in profile.missing_data.values() if v > 30)
        miss_penalty = min(high_missing * 5, 20)
        accuracy = float(max(0, 100 - dup_penalty - miss_penalty))

        overall = (
            completeness * 0.30
            + uniqueness  * 0.20
            + validity    * 0.20
            + consistency * 0.15
            + accuracy    * 0.15
        )

        return QualityMetrics(
            completeness=round(completeness, 2),
            uniqueness=round(uniqueness, 2),
            validity=round(validity, 2),
            consistency=round(consistency, 2),
            accuracy=round(accuracy, 2),
            overall_quality_score=round(overall, 2),
        )

    # ------------------------------------------------------------------
    # Private: statistical summary
    # ------------------------------------------------------------------

    def _statistical_summary(self, df: pd.DataFrame) -> Dict:
        """Return per-column descriptive stats for all numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        summary: Dict = {}
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            summary[col] = {
                "mean":       _safe_float(series.mean()),
                "median":     _safe_float(series.median()),
                "std":        _safe_float(series.std()),
                "min":        _safe_float(series.min()),
                "max":        _safe_float(series.max()),
                "q25":        _safe_float(series.quantile(0.25)),
                "q75":        _safe_float(series.quantile(0.75)),
                "skewness":   _safe_float(series.skew()),
                "kurtosis":   _safe_float(series.kurtosis()),
                "null_count": int(numeric_df[col].isnull().sum()),
            }
        return summary

    # ------------------------------------------------------------------
    # Private: missing data analysis
    # ------------------------------------------------------------------

    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict:
        """Identify missing-data patterns and suggest imputation strategies."""
        missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
        missing_pct = missing_pct[missing_pct > 0]

        return {
            "columns_with_missing": {k: round(float(v), 2) for k, v in missing_pct.items()},
            "total_missing_pct":    round(float(
                df.isnull().sum().sum() / max(df.shape[0] * df.shape[1], 1) * 100
            ), 2),
            "missing_patterns":     self._detect_missing_patterns(df),
            "imputation_strategies": self._suggest_imputation(df, missing_pct),
        }

    def _detect_missing_patterns(self, df: pd.DataFrame) -> List[str]:
        """Identify rows/columns with multiple missing values (MCAR heuristic)."""
        patterns: List[str] = []
        missing_by_row = df.isnull().sum(axis=1)
        rows_multi = int((missing_by_row > 1).sum())
        if rows_multi:
            patterns.append(f"MCAR suspect: {rows_multi:,} rows have >1 missing value")
        for col in df.columns:
            n = int(df[col].isnull().sum())
            if n:
                pct = round(n / len(df) * 100, 1)
                patterns.append(f"Column '{col}': {n:,} missing ({pct}%)")
        return patterns

    def _suggest_imputation(self, df: pd.DataFrame, missing_cols: pd.Series) -> Dict:
        """Recommend simple imputation strategy per missing column."""
        strategies: Dict = {}
        for col in missing_cols.index:
            if df[col].dtype in ["int64", "float64", "int32", "float32"]:
                strategies[col] = f"Numeric → median ({df[col].median():.4g})"
            else:
                mode_vals = df[col].mode()
                mode_val  = mode_vals[0] if len(mode_vals) > 0 else "Unknown"
                strategies[col] = f"Categorical → mode ('{mode_val}')"
        return strategies

    # ------------------------------------------------------------------
    # Private: outlier detection
    # ------------------------------------------------------------------

    def _detect_outliers(self, df: pd.DataFrame) -> Dict:
        """Flag outliers per numeric column using the IQR fence method."""
        outliers: Dict = {}
        numeric_df = df.select_dtypes(include=[np.number])

        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) < 4:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask   = (series < lower) | (series > upper)
            count  = int(mask.sum())
            if count:
                pct = round(count / len(df) * 100, 2)
                outliers[col] = {
                    "count":       count,
                    "percentage":  pct,
                    "lower_fence": _safe_float(lower),
                    "upper_fence": _safe_float(upper),
                    "action":      "Flag for review" if pct < 5 else "Likely valid extreme values — keep",
                }
        return outliers

    # ------------------------------------------------------------------
    # Private: categorical analysis
    # ------------------------------------------------------------------

    def _analyze_categorical(self, df: pd.DataFrame) -> Dict:
        """Profile each categorical/object column for cardinality and balance."""
        cat_df = df.select_dtypes(include=["object"])
        analysis: Dict = {}
        for col in cat_df.columns:
            vc = df[col].value_counts(dropna=True)
            imbalance = float(vc.max() / vc.min()) if len(vc) > 1 and vc.min() > 0 else float("inf")
            analysis[col] = {
                "unique_values":  int(df[col].nunique()),
                "top_values":     vc.head(5).to_dict(),
                "imbalance_ratio": round(imbalance, 2),
                "null_count":     int(df[col].isnull().sum()),
            }
        return analysis

    # ------------------------------------------------------------------
    # Private: correlation analysis
    # ------------------------------------------------------------------

    def _analyze_correlations(self, df: pd.DataFrame) -> Dict:
        """Compute Pearson correlation matrix and flag high-correlation pairs (>0.7)."""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return {"message": "Fewer than 2 numeric columns — correlation analysis skipped."}

        corr_matrix = numeric_df.corr()
        high_corr: List[Dict] = []
        cols = corr_matrix.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.7:
                    high_corr.append({
                        "col1":        cols[i],
                        "col2":        cols[j],
                        "correlation": round(float(val), 4),
                    })

        return {
            "high_correlations":        high_corr,
            "correlation_matrix":       {
                col: {r: _safe_float(v) for r, v in corr_matrix[col].items()}
                for col in cols
            },
            "multicollinearity_warning": len(high_corr) > 0,
        }

    # ------------------------------------------------------------------
    # Private: recommendations, cleaning steps, warnings
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self,
        profile:      DataProfile,
        quality:      QualityMetrics,
        missing:      Dict,
        outliers:     Dict,
        categorical:  Dict,
        correlations: Dict,
    ) -> List[str]:
        recs: List[str] = []

        # Quality-based
        if quality.overall_quality_score < 50:
            recs.append("⚠ CRITICAL: Data quality very low (<50/100). Review before any analysis.")
        elif quality.overall_quality_score < self.QUALITY_THRESHOLD:
            recs.append("⚠ Data quality moderate — preprocessing recommended before analysis.")

        # Missing data
        total_miss = missing.get("total_missing_pct", 0)
        if total_miss > 30:
            recs.append(f"⚠ {total_miss:.1f}% of all values are missing — significant data-loss risk.")
        elif total_miss > 10:
            recs.append(f"⚠ {total_miss:.1f}% missing values detected — review imputation strategy.")

        # Duplicates
        if profile.duplicates > 0:
            recs.append(f"⚠ {profile.duplicates:,} duplicate rows found — remove before analysis.")

        # Outliers
        if len(outliers) > 3:
            recs.append(f"⚠ Outliers detected in {len(outliers)} columns — review before statistical tests.")

        # Categorical imbalance
        for col, info in categorical.items():
            if info["imbalance_ratio"] > 10:
                recs.append(
                    f"⚠ Column '{col}' is highly imbalanced ({info['imbalance_ratio']:.1f}:1) "
                    "— consider stratified sampling."
                )

        # Multicollinearity
        if correlations.get("multicollinearity_warning"):
            pairs = correlations.get("high_correlations", [])
            for p in pairs[:3]:  # Show first 3 pairs
                recs.append(
                    f"⚠ High correlation: '{p['col1']}' ↔ '{p['col2']}' = {p['correlation']:.2f} "
                    "— consider dropping one or engineering a ratio feature."
                )

        # Standard positive recommendations
        recs.append("✓ Standardise numeric features (z-score / min-max) for distance-based algorithms.")
        recs.append("✓ Encode categorical variables (one-hot or ordinal encoding).")
        recs.append("✓ Apply train/test split *after* preprocessing to avoid leakage.")

        return recs

    def _get_cleaning_steps(self, missing: Dict) -> List[str]:
        steps: List[str] = []
        n = 1
        for col, strategy in missing.get("imputation_strategies", {}).items():
            steps.append(f"{n}. Impute '{col}': {strategy}")
            n += 1
        steps.append(f"{n}. Remove exact duplicate rows.")
        n += 1
        steps.append(f"{n}. Standardise column names (lowercase, underscores, no spaces).")
        n += 1
        steps.append(f"{n}. Convert mistyped numeric strings to float/int.")
        n += 1
        steps.append(f"{n}. Consolidate rare categories (frequency <1%) into 'Other'.")
        return steps

    def _generate_warnings(
        self,
        profile:  DataProfile,
        quality:  QualityMetrics,
        missing:  Dict,
        outliers: Dict,
    ) -> List[str]:
        warnings: List[str] = []
        if profile.duplicates > 0:
            warnings.append(f"⚠ {profile.duplicates:,} duplicate rows found.")
        if quality.completeness < 80:
            warnings.append(
                f"⚠ Completeness is only {quality.completeness:.1f}% (target ≥ 95%)."
            )
        total_miss = missing.get("total_missing_pct", 0)
        if total_miss > 30:
            warnings.append(f"⚠ Over 30% total missing values ({total_miss:.1f}%) — significant data-loss risk.")
        if len(outliers) > 5:
            warnings.append(f"⚠ {len(outliers)} columns contain outliers — review each before modelling.")
        return warnings

    # ------------------------------------------------------------------
    # Private: report formatters
    # ------------------------------------------------------------------

    def _format_missing_section(self, missing: Dict) -> str:
        cols = missing.get("columns_with_missing", {})
        if not cols:
            return "No missing values detected ✓"
        lines = [f"Total missing: **{missing.get('total_missing_pct', 0):.2f}%**\n"]
        for col, pct in cols.items():
            icon = "❌" if pct > 20 else "⚠"
            lines.append(f"- {icon} **{col}**: {pct:.2f}% missing")

        strategies = missing.get("imputation_strategies", {})
        if strategies:
            lines.append("\n**Suggested imputation:**")
            for col, strat in strategies.items():
                lines.append(f"- `{col}`: {strat}")
        return "\n".join(lines)

    def _format_stats_section(self, stats: Dict) -> str:
        if not stats:
            return "No numeric columns found."
        lines: List[str] = []
        for col, v in stats.items():
            lines.append(f"\n### {col}")
            lines.append(f"| Stat | Value |")
            lines.append(f"|---|---|")
            lines.append(f"| Mean | {v['mean']:.4g} |")
            lines.append(f"| Median | {v['median']:.4g} |")
            lines.append(f"| Std Dev | {v['std']:.4g} |")
            lines.append(f"| Min | {v['min']:.4g} |")
            lines.append(f"| Max | {v['max']:.4g} |")
            lines.append(f"| Q25 | {v['q25']:.4g} |")
            lines.append(f"| Q75 | {v['q75']:.4g} |")
            lines.append(f"| Skewness | {v['skewness']:.4g} |")
            lines.append(f"| Kurtosis | {v['kurtosis']:.4g} |")
            lines.append(f"| Null count | {v['null_count']:,} |")
        return "\n".join(lines)

    def _format_outliers_section(self, outliers: Dict) -> str:
        if not outliers:
            return "No significant outliers detected ✓"
        lines: List[str] = []
        for col, info in outliers.items():
            lines.append(
                f"- **{col}**: {info['count']:,} outliers ({info['percentage']:.2f}%) "
                f"| Fence [{info['lower_fence']:.4g}, {info['upper_fence']:.4g}] "
                f"| *{info['action']}*"
            )
        return "\n".join(lines)

    def _format_categorical_section(self, categorical: Dict) -> str:
        if not categorical:
            return "No categorical columns found."
        lines: List[str] = []
        for col, info in categorical.items():
            lines.append(f"\n### {col}")
            lines.append(f"- Unique values: **{info['unique_values']:,}**")
            ir = info["imbalance_ratio"]
            ir_str = f"{ir:.2f}:1" if ir != float("inf") else "∞ (only one category)"
            lines.append(f"- Imbalance ratio: {ir_str}")
            top = list(info["top_values"].items())[:5]
            lines.append("- Top values: " + ", ".join(f"'{k}' ({v:,})" for k, v in top))
            if info["null_count"]:
                lines.append(f"- Nulls: {info['null_count']:,}")
        return "\n".join(lines)

    def _format_correlation_section(self, corr: Dict) -> str:
        if corr.get("message"):
            return corr["message"]
        pairs = corr.get("high_correlations", [])
        if not pairs:
            return "No high correlations (>0.7) detected ✓"
        lines = ["High-correlation pairs (|r| > 0.7):"]
        for p in pairs:
            lines.append(f"- **{p['col1']}** ↔ **{p['col2']}**: r = {p['correlation']:.4f}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val) -> float:
    """Convert a numpy scalar to a plain Python float, handling NaN/Inf."""
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return 0.0
        return round(f, 6)
    except (TypeError, ValueError):
        return 0.0
