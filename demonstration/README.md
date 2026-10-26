# ARIA / Orchestra Demonstrations 🎯

This directory contains standalone, reproducible demonstrations showcasing the capabilities of the ARIA World-Class Agent Suite.

---

## 1. Pulse Database Analytics & Performance Audit (`demonstration/pulse_analytics/`)
Showcases remote source discovery, DuckDB SQL extraction, behavioral profiling, and Anthropic DOCX executive reporting:
* **`data/`**: Synthetic sample daily logs, user accounts, and predictive scores.
* **`scripts/`**: 
  - `arthur_mongo_discovery.py` — Schema discovery and extraction from MongoDB.
  - `analyze_user_performance.py` — DuckDB analytical joins and cohort metrics.
  - `generate_pulse_charts.py` — 300 DPI regression and ranking plots.
  - `generate_pulse_docx_report.py` — Compiles executive Word deliverable.
* **`reports/`**: [`Sample_Pulse_Performance_and_Behavioral_Audit_Report.docx`](reports/Sample_Pulse_Performance_and_Behavioral_Audit_Report.docx) (489 KB).
* **`assets/`**: High-resolution diagnostic figures.

---

## 2. Amazon Product Rating Machine Learning Pipeline (`demonstration/amazon_product_rating/`)
Showcases the end-to-end ML lifecycle from EDA to Random Forest tournament and SHAP explainability:
* **`data/`**: Amazon product rating benchmark dataset (1,465 products).
* **`scripts/`**:
  - `eda_profile.py` — Tukey/Nightingale exploratory data analysis.
  - `preprocess.py` — Deming-inspired leak-free cleaning and train/test splits.
  - `feature_engineering.py` — Grandmaster signal extraction & selection.
  - `train_models.py` — Breiman/Chen model tournament and Optuna tuning.
  - `evaluate_model.py` — Rudin/Lundberg cynical audit & TreeSHAP governance.
  - `generate_docx_report.py` — Compiles publication Word deliverable.
* **`reports/`**: [`Amazon_Product_Rating_Analysis_Report.docx`](reports/Amazon_Product_Rating_Analysis_Report.docx) (433 KB).
* **`assets/`**: Distribution, residual, and feature importance visual plots.
