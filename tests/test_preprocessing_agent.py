"""
Tests for DataPreprocessingAgent.

Run with:
    pytest tests/test_preprocessing_agent.py -v
"""

import os
import pytest
import numpy as np
import pandas as pd

# Support running from project root or from within tests/
try:
    from agents.preprocessing_agent import DataPreprocessingAgent, EDASummary
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from agents.preprocessing_agent import DataPreprocessingAgent, EDASummary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def agent():
    return DataPreprocessingAgent()


@pytest.fixture
def sample_csv(tmp_path):
    """A small synthetic CSV with nulls, a duplicate, and outliers."""
    rng = np.random.default_rng(42)
    n = 120

    df = pd.DataFrame({
        "id":         range(1, n + 1),
        "age":        rng.integers(18, 80, n).astype(int),
        "salary":     rng.normal(50_000, 15_000, n),
        "department": rng.choice(["Sales", "IT", "HR", "Finance"], n),
        "tenure":     rng.integers(0, 30, n).astype(int),
    })

    # Inject missing values
    df.loc[5:10, "salary"] = np.nan       # 6 rows
    df.loc[15:17, "department"] = np.nan  # 3 rows

    # Inject an outlier
    df.loc[0, "salary"] = 999_999.0

    # Inject an exact duplicate
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    filepath = tmp_path / "sample.csv"
    df.to_csv(filepath, index=False)
    return str(filepath)


@pytest.fixture
def clean_csv(tmp_path):
    """A completely clean CSV with no issues."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "x": rng.normal(0, 1, 200),
        "y": rng.normal(5, 2, 200),
        "label": rng.choice(["A", "B"], 200),
    })
    path = tmp_path / "clean.csv"
    df.to_csv(path, index=False)
    return str(path)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class TestLoadData:
    def test_csv_loads_correctly(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] > 0
        assert df.shape[1] > 0

    def test_missing_file_raises(self, agent):
        with pytest.raises(Exception):
            agent._load_data("nonexistent_file.csv")


# ---------------------------------------------------------------------------
# Data profiling
# ---------------------------------------------------------------------------

class TestProfileData:
    def test_shape_matches(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert profile.shape == df.shape

    def test_detects_duplicates(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert profile.duplicates >= 1

    def test_numeric_cols_identified(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert "salary" in profile.numeric_cols
        assert "age" in profile.numeric_cols

    def test_categorical_cols_identified(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert "department" in profile.categorical_cols

    def test_missing_data_recorded(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert "salary" in profile.missing_data
        assert "department" in profile.missing_data

    def test_memory_positive(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        assert profile.memory_mb > 0


# ---------------------------------------------------------------------------
# Quality metrics
# ---------------------------------------------------------------------------

class TestQualityMetrics:
    def test_overall_score_in_range(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        quality = agent._assess_quality(df, profile)
        assert 0 <= quality.overall_quality_score <= 100

    def test_completeness_reflects_nulls(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        profile = agent._profile_data(df)
        quality = agent._assess_quality(df, profile)
        assert quality.completeness < 100  # we injected nulls

    def test_clean_data_high_score(self, agent, clean_csv):
        df = agent._load_data(clean_csv)
        profile = agent._profile_data(df)
        quality = agent._assess_quality(df, profile)
        assert quality.overall_quality_score >= 70


# ---------------------------------------------------------------------------
# Statistical summary
# ---------------------------------------------------------------------------

class TestStatisticalSummary:
    def test_salary_stats_present(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        stats = agent._statistical_summary(df)
        assert "salary" in stats
        assert "mean" in stats["salary"]
        assert "median" in stats["salary"]
        assert "skewness" in stats["salary"]

    def test_no_nan_in_stats(self, agent, sample_csv):
        import math
        df = agent._load_data(sample_csv)
        stats = agent._statistical_summary(df)
        for col, values in stats.items():
            for k, v in values.items():
                if isinstance(v, float):
                    assert not math.isnan(v), f"{col}.{k} is NaN"


# ---------------------------------------------------------------------------
# Missing data analysis
# ---------------------------------------------------------------------------

class TestMissingDataAnalysis:
    def test_detects_salary_missing(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        missing = agent._analyze_missing_data(df)
        assert "salary" in missing["columns_with_missing"]

    def test_detects_department_missing(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        missing = agent._analyze_missing_data(df)
        assert "department" in missing["columns_with_missing"]

    def test_total_missing_pct_positive(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        missing = agent._analyze_missing_data(df)
        assert missing["total_missing_pct"] > 0

    def test_imputation_strategies_present(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        missing = agent._analyze_missing_data(df)
        assert "salary" in missing["imputation_strategies"]
        assert "department" in missing["imputation_strategies"]

    def test_no_missing_clean_data(self, agent, clean_csv):
        df = agent._load_data(clean_csv)
        missing = agent._analyze_missing_data(df)
        assert missing["total_missing_pct"] == 0.0


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------

class TestOutlierDetection:
    def test_detects_salary_outlier(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        outliers = agent._detect_outliers(df)
        # We injected salary = 999_999, which is a massive outlier
        assert "salary" in outliers

    def test_outlier_count_positive(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        outliers = agent._detect_outliers(df)
        assert outliers["salary"]["count"] >= 1

    def test_outlier_percentage_sane(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        outliers = agent._detect_outliers(df)
        for col, info in outliers.items():
            assert 0 < info["percentage"] <= 100


# ---------------------------------------------------------------------------
# Categorical analysis
# ---------------------------------------------------------------------------

class TestCategoricalAnalysis:
    def test_department_analysed(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        cat = agent._analyze_categorical(df)
        assert "department" in cat

    def test_unique_values_positive(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        cat = agent._analyze_categorical(df)
        assert cat["department"]["unique_values"] >= 1

    def test_top_values_present(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        cat = agent._analyze_categorical(df)
        assert len(cat["department"]["top_values"]) >= 1


# ---------------------------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------------------------

class TestCorrelationAnalysis:
    def test_returns_dict(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        corr = agent._analyze_correlations(df)
        assert isinstance(corr, dict)

    def test_message_when_too_few_cols(self, agent):
        df = pd.DataFrame({"only_col": [1, 2, 3]})
        corr = agent._analyze_correlations(df)
        assert "message" in corr

    def test_matrix_populated(self, agent, sample_csv):
        df = agent._load_data(sample_csv)
        corr = agent._analyze_correlations(df)
        if "correlation_matrix" in corr:
            assert len(corr["correlation_matrix"]) >= 1


# ---------------------------------------------------------------------------
# Full pipeline — preprocess_data
# ---------------------------------------------------------------------------

class TestPreprocessData:
    def test_returns_eda_summary(self, agent, sample_csv):
        summary = agent.preprocess_data(sample_csv, task_id=99)
        assert isinstance(summary, EDASummary)

    def test_timestamp_set(self, agent, sample_csv):
        summary = agent.preprocess_data(sample_csv)
        assert summary.timestamp  # non-empty

    def test_recommendations_list(self, agent, sample_csv):
        summary = agent.preprocess_data(sample_csv)
        assert isinstance(summary.recommendations, list)
        assert len(summary.recommendations) > 0

    def test_cleaning_steps_list(self, agent, sample_csv):
        summary = agent.preprocess_data(sample_csv)
        assert isinstance(summary.cleaning_steps, list)
        assert len(summary.cleaning_steps) > 0

    def test_readiness_flag_is_bool(self, agent, sample_csv):
        summary = agent.preprocess_data(sample_csv)
        assert isinstance(summary.is_ready_for_analysis, bool)

    def test_clean_data_is_ready(self, agent, clean_csv):
        summary = agent.preprocess_data(clean_csv)
        # Clean data should pass the quality gate
        assert summary.is_ready_for_analysis is True


# ---------------------------------------------------------------------------
# EDA report generation
# ---------------------------------------------------------------------------

class TestGenerateEDAReport:
    def test_report_file_created(self, agent, sample_csv, tmp_path):
        summary = agent.preprocess_data(sample_csv)
        output = str(tmp_path / "report.md")
        agent.generate_eda_report(summary, output)
        assert os.path.exists(output)

    def test_report_contains_key_sections(self, agent, sample_csv, tmp_path):
        summary = agent.preprocess_data(sample_csv)
        output = str(tmp_path / "report.md")
        agent.generate_eda_report(summary, output)
        text = open(output, encoding="utf-8").read()
        for section in [
            "Exploratory Data Analysis",
            "Data Profile",
            "Data Quality Score",
            "Missing Data",
            "Statistical Summary",
            "Outliers",
            "Categorical",
            "Correlation",
            "Recommendations",
            "Data Readiness",
        ]:
            assert section in text, f"Section '{section}' missing from report"

    def test_report_returned_as_string(self, agent, sample_csv, tmp_path):
        summary = agent.preprocess_data(sample_csv)
        output = str(tmp_path / "report2.md")
        result = agent.generate_eda_report(summary, output)
        assert isinstance(result, str)
        assert len(result) > 100
