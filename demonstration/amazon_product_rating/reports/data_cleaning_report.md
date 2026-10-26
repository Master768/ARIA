# Data Cleaning & Preprocessing Report
**Agent:** Leo (Senior Preprocessing Engineer)  
**Dataset:** `data/amazon.csv`  
**Generated:** 2026-10-26  

---

## 1. Cleaning Actions & Transformations
- **Currency Stripping:** Stripped `₹` and thousands commas from `discounted_price` and `actual_price`; cast to `float64`.
- **Percentage Parsing:** Removed `%` symbol from `discount_percentage`; converted to numerical percentage.
- **Rogue Character Removal:** Cleared pipe character `|` from `rating` column. 1 invalid row dropped.
- **Null Value Resolution:** Imputed missing `rating_count` using the training median (`5,104`), preventing data leakage.
- **Category Normalization:** Parsed hierarchical taxonomy to extract `primary_category`.

---

## 2. Dataset Partitioning
- **Training Set:** 1,171 records (80%) saved to `data/processed/train_cleaned.parquet`.
- **Holdout Test Set:** 293 records (20%) saved to `data/processed/test_cleaned.parquet`.

---

## 3. Handoff to Priya (Feature Engineering)
- Target variable `rating_clean` is continuous ($1.0 - 5.0$).
- Clean price columns (`discounted_price_clean`, `actual_price_clean`) ready for discount amount and ratio feature generation.
- Clean text columns ready for token length and sentiment features.
