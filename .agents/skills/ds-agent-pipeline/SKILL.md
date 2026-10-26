---
name: ds-agent-pipeline
description: End-to-End Enterprise Data Science & ML Pipeline Orchestrator. Coordinates the 8 expert agents from Source Discovery & SQL Extraction (Arthur, Silas) to EDA, Preprocessing, Features, Modeling, Evaluation, and Storytelling (Maya, Leo, Priya, Julian, Elena, Marcus). Use when running an end-to-end data pipeline.
---

# End-to-End Enterprise Data Science Pipeline Orchestrator

## Overview

The **Enterprise Data Science Pipeline Orchestrator** automates and coordinates the complete, disciplined 8-stage Data Science and Machine Learning lifecycle:

```
[1. Arthur] Data Source Discovery & Catalog Navigation (Kimball)
   ↓
[2. Silas] SQL Architecture & Dataset Extraction (Celko / DuckDB)
   ↓
[3. Maya] Data Understanding & Exploration (Tukey)
   ↓
[4. Leo] Data Cleaning & Leak-Free Preprocessing (Deming)
   ↓
[5. Priya] Feature Engineering & Signal Selection (Kaggle Grandmasters)
   ↓
[6. Julian] Model Building & Optuna Hyperparameter Tuning (Breiman & Chen)
   ↓
[7. Elena] Model Evaluation, SHAP & Governance Audit (Rudin & Lundberg)
   ↓
[8. Marcus] Executive Storytelling & Publication (Tufte & Minto / Anthropic DOCX)
```

---

## The 8 Expert Agents in Sequence

| Phase | Agent Persona | World-Class Mentor Inspiration | Skill Name | Primary Responsibility | Artifact Handoff |
|---|---|---|---|---|---|
| **Phase 1** | **Arthur** | Ralph Kimball | `ds-agent-source-locator` | Identifies databases, navigates data catalogs, maps ER schemas, and pinpoints source tables. | `data/source_discovery_manifest.md` |
| **Phase 2** | **Silas** | Joe Celko | `ds-agent-sql-query-engineer` | Writes optimized CTE SQL (DuckDB, Postgres, Snowflake), executes extraction, exports clean Parquet. | `data/raw/[dataset].parquet`, `data/extraction_audit_report.md` |
| **Phase 3** | **Maya** | John Tukey & Florence Nightingale | `ds-agent-data-understanding` | Statistical profiling, distribution moments, VIF, MCAR tests, UMAP, and Isolation Forests. | `data/data_understanding_report.md` |
| **Phase 4** | **Leo** | W. Edwards Deming | `ds-agent-data-cleaning` | Leak-free splitting, Winsorization, MICE/KNN imputation, smoothed target encoding, pipeline serialization. | `data/processed/train_cleaned.parquet`, `models/preprocessor.joblib` |
| **Phase 5** | **Priya** | Top Kaggle Grandmasters | `ds-agent-feature-engineering` | Cyclical time transforms, Out-of-Fold group aggregations, non-linear interactions, 4-stage selection cascade. | `data/features/X_train.parquet`, `data/feature_engineering_report.md` |
| **Phase 6** | **Julian** | Leo Breiman & Tianqi Chen | `ds-agent-model-building` | Baseline benchmarking, multi-algorithm tournament (RF, HistGB, LightGBM, XGBoost, CatBoost), Optuna tuning. | `models/champion_model.joblib`, `models/model_training_report.md` |
| **Phase 7** | **Elena** | Cynthia Rudin & Scott Lundberg | `ds-agent-model-evaluation` | PR-AUC, Brier score, calibration curves, SHAP explainability, cohort error slicing, and governance sign-off. | `reports/published/model_evaluation_report.md` |
| **Phase 8** | **Marcus** | Edward Tufte & Barbara Minto | `ds-agent-storytelling` | Minto Pyramid synthesis, data-to-ink ratio graphics, executive presentation decks, and Anthropic Word (.docx) reports. | `reports/published/[Project]_Report.docx` |

---

## Execution Modes

1. **Full Autonomous End-to-End Pipeline**:
   - Instruct the agent: *"Find customer churn data, extract it via SQL, build the ML model, and generate the executive report"*.
   - Sequence: Arthur ➔ Silas ➔ Maya ➔ Leo ➔ Priya ➔ Julian ➔ Elena ➔ Marcus.
   - Pauses at the **Human Confirmation Gate** before generating the final Word `.docx` report.

2. **Upstream Data Ingestion Only**:
   - *"Arthur, locate where our transaction and customer tables live"* ➔ `ds-agent-source-locator`
   - *"Silas, write an optimized DuckDB SQL query to join orders with customers"* ➔ `ds-agent-sql-query-engineer`

3. **Downstream Modeling & Storytelling Only**:
   - Run any individual agent on demand (Maya, Leo, Priya, Julian, Elena, or Marcus).

---

## Core Invariants
1. **Zero Data Leakage:** Preprocessors and feature aggregations fit strictly on the training partition.
2. **Reproducible Code First:** Every stage produces a self-contained Python or SQL script in `scripts/`.
3. **Optimized SQL Execution:** Zero `SELECT *`, sargable filters, and zero division-by-zero crashes.
4. **Independent Audit Gate:** No model is marked production-ready without Elena's evaluation sign-off.
5. **Human Confirmation Before Publishing:** No final Word `.docx` report is generated without explicit user approval.
6. **Zero Raw LaTeX:** All mathematical relationships, metrics, and feature transformations are formatted as clean inline code spans (e.g. `FamilySize = SibSp + Parch + 1`) or clean Unicode text. Raw LaTeX (`$...$`, `\text{...}`, `\frac{...}`) is strictly prohibited across all reports, slides, and chat outputs.
