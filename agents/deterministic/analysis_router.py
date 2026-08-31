import logging
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger("analysis_router")

class AlgorithmicAnalysisRouter:
    @staticmethod
    def recommend_techniques(df_profile: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        q_lower = user_query.lower()
        num_cols = df_profile.get("numeric_columns", [])
        cat_cols = df_profile.get("categorical_columns", [])

        matched_num = [c for c in num_cols if c.lower() in q_lower]
        matched_cat = [c for c in cat_cols if c.lower() in q_lower]

        chart_type = "bar"
        recommended_stats = ["mean", "median", "std", "quartiles"]
        code_snippet = ""

        if len(matched_num) >= 2 or ("correlation" in q_lower and len(num_cols) >= 2):
            col1 = matched_num[0] if matched_num else num_cols[0]
            col2 = matched_num[1] if len(matched_num) > 1 else num_cols[1]
            chart_type = "scatter"
            recommended_stats = ["pearson_correlation", "covariance", "regression_slope"]
            code_snippet = f"sns.scatterplot(data=df, x='{col1}', y='{col2}')"

        elif matched_cat and matched_num:
            cat = matched_cat[0]
            num = matched_num[0]
            chart_type = "bar" if "top" in q_lower or "sum" in q_lower else "boxplot"
            recommended_stats = ["group_means", "group_sums", "anova_f_stat"]
            code_snippet = f"sns.barplot(data=df.groupby('{cat}')['{num}'].sum().reset_index().head(10), x='{cat}', y='{num}')"

        elif matched_num or "distribution" in q_lower:
            num = matched_num[0] if matched_num else (num_cols[0] if num_cols else "")
            chart_type = "histogram"
            recommended_stats = ["mean", "std", "skewness", "kurtosis"]
            code_snippet = f"sns.histplot(df['{num}'], kde=True)"

        elif matched_cat:
            cat = matched_cat[0]
            chart_type = "bar"
            recommended_stats = ["mode", "frequency_counts", "percentage"]
            code_snippet = f"df['{cat}'].value_counts().head(10).plot(kind='bar')"

        return {
            "recommended_chart_type": chart_type,
            "recommended_stats": recommended_stats,
            "matched_numeric_cols": matched_num,
            "matched_categorical_cols": matched_cat,
            "suggested_seaborn_code": code_snippet
        }
