"""
Phase 2: Data Cleaning & Preprocessing Script
Agent: Leo (Senior Preprocessing Engineer)
Dataset: data/amazon.csv -> data/processed/
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def clean_currency(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace('₹', '').replace(',', '').strip()
    try:
        return float(s)
    except:
        return np.nan

def clean_percentage(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace('%', '').strip()
    try:
        return float(s)
    except:
        return np.nan

def clean_rating(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace('|', '').strip()
    try:
        return float(s)
    except:
        return np.nan

def clean_count(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace(',', '').strip()
    try:
        return float(s)
    except:
        return np.nan

def main():
    print("--- [Leo] Starting Data Cleaning & Preprocessing ---")
    raw_path = "data/amazon.csv"
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # 1. Clean numerical fields
    df['discounted_price_clean'] = df['discounted_price'].apply(clean_currency)
    df['actual_price_clean'] = df['actual_price'].apply(clean_currency)
    df['discount_percentage_clean'] = df['discount_percentage'].apply(clean_percentage)
    df['rating_clean'] = df['rating'].apply(clean_rating)
    df['rating_count_clean'] = df['rating_count'].apply(clean_count)
    
    # Drop rows where target rating is NaN (e.g. rogue row)
    df_clean = df.dropna(subset=['rating_clean']).copy()
    rows_dropped_target = initial_rows - len(df_clean)
    print(f"Dropped {rows_dropped_target} rows due to invalid target 'rating'. Remaining: {len(df_clean)}")
    
    # 2. Extract Primary Category
    df_clean['primary_category'] = df_clean['category'].astype(str).apply(
        lambda x: x.split('|')[0].strip() if '|' in x else x.strip()
    )
    
    # 3. Clean Text lengths
    df_clean['about_product_text'] = df_clean['about_product'].fillna('').astype(str)
    df_clean['review_title_text'] = df_clean['review_title'].fillna('').astype(str)
    df_clean['review_content_text'] = df_clean['review_content'].fillna('').astype(str)
    
    # 4. Train / Test Split (Strict Leak-Free Principle)
    train_df, test_df = train_test_split(df_clean, test_size=0.20, random_state=42)
    print(f"Train split: {len(train_df):,} rows | Test split: {len(test_df):,} rows")
    
    # Impute missing rating_count using Train median only
    median_rating_count = train_df['rating_count_clean'].median()
    train_df['rating_count_clean'] = train_df['rating_count_clean'].fillna(median_rating_count)
    test_df['rating_count_clean'] = test_df['rating_count_clean'].fillna(median_rating_count)
    
    # 5. Save Clean Datasets
    os.makedirs("data/processed", exist_ok=True)
    train_df.to_parquet("data/processed/train_cleaned.parquet", index=False)
    test_df.to_parquet("data/processed/test_cleaned.parquet", index=False)
    print("Cleaned splits saved to data/processed/train_cleaned.parquet and test_cleaned.parquet")
    
    # 6. Generate Preprocessing Report
    report_content = f"""# Data Cleaning & Preprocessing Report
**Agent:** Leo (Senior Preprocessing Engineer)  
**Dataset:** `data/amazon.csv`  
**Generated:** 2026-10-26  

---

## 1. Cleaning Actions & Transformations
- **Currency Stripping:** Stripped `₹` and thousands commas from `discounted_price` and `actual_price`; cast to `float64`.
- **Percentage Parsing:** Removed `%` symbol from `discount_percentage`; converted to numerical percentage.
- **Rogue Character Removal:** Cleared pipe character `|` from `rating` column. {rows_dropped_target} invalid row dropped.
- **Null Value Resolution:** Imputed missing `rating_count` using the training median (`{median_rating_count:,.0f}`), preventing data leakage.
- **Category Normalization:** Parsed hierarchical taxonomy to extract `primary_category`.

---

## 2. Dataset Partitioning
- **Training Set:** {len(train_df):,} records (80%) saved to `data/processed/train_cleaned.parquet`.
- **Holdout Test Set:** {len(test_df):,} records (20%) saved to `data/processed/test_cleaned.parquet`.

---

## 3. Handoff to Priya (Feature Engineering)
- Target variable `rating_clean` is continuous ($1.0 - 5.0$).
- Clean price columns (`discounted_price_clean`, `actual_price_clean`) ready for discount amount and ratio feature generation.
- Clean text columns ready for token length and sentiment features.
"""
    with open("data/data_cleaning_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("Report written to data/data_cleaning_report.md")
    print("--- [Leo] Phase 2 Completed Successfully ---")

if __name__ == "__main__":
    main()
