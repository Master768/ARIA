"""
Phase 1: Data Understanding & Exploration Script
Agent: Maya (Lead Exploratory Data Scientist)
Dataset: data/amazon.csv
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("--- [Maya] Starting Data Understanding & Exploration ---")
    data_path = "data/amazon.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    df = pd.read_csv(data_path)
    n_rows, n_cols = df.shape
    print(f"Dataset Loaded: {n_rows:,} rows, {n_cols} columns")
    
    # 1. Missingness & Type Analysis
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / n_rows) * 100
    
    type_info = []
    for col in df.columns:
        type_info.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "null_count": int(missing_counts[col]),
            "null_pct": round(missing_pct[col], 2),
            "unique_count": int(df[col].nunique()),
            "sample_val": str(df[col].dropna().iloc[0])[:40] if not df[col].dropna().empty else "N/A"
        })
    profile_df = pd.DataFrame(type_info)
    
    # 2. Rating distribution exploration
    # Clean rating temporarily just for exploration
    clean_rating = pd.to_numeric(df['rating'].astype(str).str.replace('|', '', regex=False), errors='coerce')
    rating_mean = clean_rating.mean()
    rating_median = clean_rating.median()
    rating_std = clean_rating.std()
    rating_skew = clean_rating.skew()
    print(f"Rating Stats: Mean={rating_mean:.2f}, Median={rating_median:.2f}, Std={rating_std:.2f}, Skew={rating_skew:.2f}")
    
    # 3. Category inspection
    df['main_category'] = df['category'].astype(str).apply(lambda x: x.split('|')[0] if '|' in x else x)
    top_categories = df['main_category'].value_counts().head(8)
    
    # 4. Generate EDA Visualizations
    os.makedirs("reports/assets", exist_ok=True)
    
    # Chart 1: Rating Distribution
    plt.figure(figsize=(9, 5), dpi=300)
    sns.set_theme(style="whitegrid")
    sns.histplot(clean_rating.dropna(), bins=20, kde=True, color="#2b5c8f", edgecolor="black")
    plt.axvline(rating_mean, color="#d9534f", linestyle="--", linewidth=2, label=f"Mean: {rating_mean:.2f}")
    plt.axvline(rating_median, color="#5cb85c", linestyle="-", linewidth=2, label=f"Median: {rating_median:.2f}")
    plt.title("Distribution of Amazon Product Ratings", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Rating (1.0 - 5.0)", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig("reports/assets/eda_rating_distribution.png")
    plt.close()
    
    # Chart 2: Top Main Categories
    plt.figure(figsize=(10, 5), dpi=300)
    sns.barplot(x=top_categories.values, y=top_categories.index, palette="Blues_r")
    plt.title("Top Product Categories by Volume", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Number of Products", fontsize=11)
    plt.tight_layout()
    plt.savefig("reports/assets/eda_top_categories.png")
    plt.close()
    print("EDA Visualizations saved to reports/assets/")

    # 5. Write Data Understanding Report
    report_content = f"""# Data Understanding & Exploration Report
**Agent:** Maya (Lead Exploratory Data Scientist)  
**Dataset:** `data/amazon.csv`  
**Generated:** 2026-10-26  

---

## 1. Executive Summary
- **Dataset Dimensions:** {n_rows:,} rows × {n_cols} columns.
- **Target Variable Identified:** `rating` (Continuous scale 1.0 – 5.0).
- **Target Distribution:** Mean = `{rating_mean:.2f}`, Median = `{rating_median:.2f}`, Std = `{rating_std:.2f}`, Skewness = `{rating_skew:.2f}` (Left-skewed towards high ratings).
- **Duplicate Records:** {df.duplicated().sum()} exact duplicate rows.

---

## 2. Data Dictionary & Schema Profile

| Column | Data Type | Null Count | Null % | Unique Values | Sample Value |
|---|---|---|---|---|---|
"""
    for _, row in profile_df.iterrows():
        report_content += f"| `{row['column']}` | `{row['dtype']}` | {row['null_count']} | {row['null_pct']}% | {row['unique_count']:,} | `{row['sample_val']}` |\n"
        
    report_content += f"""
---

## 3. Data Quality & Preprocessing Red Flags
1. **Currency & Formatting Pollution:** `discounted_price` and `actual_price` contain Indian Rupee currency symbols (`₹`) and comma thousand separators (e.g. `₹1,099`). They must be converted to float.
2. **Percentage Formatting:** `discount_percentage` is stored as text with `%` signs (e.g. `50%`).
3. **Invalid Characters in Numeric Fields:** The `rating` column contains non-numeric character anomalies (e.g. `|` pipe characters in rogue records).
4. **Rating Count Formatting:** `rating_count` contains commas as thousands separators (e.g. `24,269`) and has {df['rating_count'].isnull().sum()} missing values.
5. **Hierarchical Categorical Strings:** `category` uses pipe-separated taxomomies (`Electronics|Cables|...`). Primary categories need parsing.

---

## 4. Visual Evidence
![Rating Distribution](assets/eda_rating_distribution.png)
*Figure 1: Distribution of Amazon Product Ratings (Mean: {rating_mean:.2f}, Median: {rating_median:.2f}).*

![Top Categories](assets/eda_top_categories.png)
*Figure 2: Distribution of Top Categories in the Dataset.*

---

## 5. Handoff to Leo (Data Cleaning & Preprocessing)
- **Priority 1:** Strip currency symbols and parse `actual_price`, `discounted_price`, and `discount_percentage` to `float32`.
- **Priority 2:** Clean `rating` column into numeric, removing rogue rows with non-numeric values.
- **Priority 3:** Impute missing `rating_count` with median after numeric casting.
- **Priority 4:** Extract `primary_category` from `category`.
"""
    with open("data/data_understanding_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("Report written to data/data_understanding_report.md")
    print("--- [Maya] Phase 1 Completed Successfully ---")

if __name__ == "__main__":
    main()
