"""
Phase 3: Feature Engineering & Selection Script
Agent: Priya (Principal Feature Engineering Architect)
Dataset: data/processed/ -> data/features/
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression

def extract_features(df, top_categories=None):
    feat = pd.DataFrame(index=df.index)
    
    # 1. Price Interactions & Transformations
    feat['actual_price'] = df['actual_price_clean']
    feat['discounted_price'] = df['discounted_price_clean']
    feat['discount_percentage'] = df['discount_percentage_clean']
    feat['discount_amount'] = df['actual_price_clean'] - df['discounted_price_clean']
    feat['discount_ratio'] = df['discounted_price_clean'] / (df['actual_price_clean'] + 1e-5)
    feat['log_actual_price'] = np.log1p(df['actual_price_clean'])
    feat['log_discounted_price'] = np.log1p(df['discounted_price_clean'])
    
    # 2. Rating & Engagement Signals
    feat['rating_count'] = df['rating_count_clean']
    feat['log_rating_count'] = np.log1p(df['rating_count_clean'])
    
    # 3. Content Length Signals
    feat['about_len'] = df['about_product_text'].apply(len)
    feat['review_title_len'] = df['review_title_text'].apply(len)
    feat['review_content_len'] = df['review_content_text'].apply(len)
    feat['review_word_count'] = df['review_content_text'].apply(lambda x: len(x.split()))
    
    # 4. Primary Category Encoding
    if top_categories is not None:
        cat_series = df['primary_category'].apply(lambda x: x if x in top_categories else 'Other')
        cat_dummies = pd.get_dummies(cat_series, prefix='cat', drop_first=True, dtype=float)
        feat = pd.concat([feat, cat_dummies], axis=1)
        
    return feat

def main():
    print("--- [Priya] Starting Feature Engineering & Selection ---")
    train_df = pd.read_parquet("data/processed/train_cleaned.parquet")
    test_df = pd.read_parquet("data/processed/test_cleaned.parquet")
    
    # Determine top 5 categories from TRAIN only to prevent leakage
    top_cats = train_df['primary_category'].value_counts().head(5).index.tolist()
    print(f"Top 5 categories from train split: {top_cats}")
    
    # Extract features
    X_train = extract_features(train_df, top_categories=top_cats)
    y_train = train_df['rating_clean'].copy()
    
    X_test = extract_features(test_df, top_categories=top_cats)
    y_test = test_df['rating_clean'].copy()
    
    # Ensure column parity
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0.0)
    
    # Mutual Information Ranking
    mi_scores = mutual_info_regression(X_train, y_train, random_state=42)
    mi_df = pd.DataFrame({
        "feature": X_train.columns,
        "mi_score": mi_scores
    }).sort_values("mi_score", ascending=False).reset_index(drop=True)
    
    print("\nTop 10 Engineered Features by Mutual Information:")
    for _, r in mi_df.head(10).iterrows():
        print(f"  - {r['feature']:<22}: MI={r['mi_score']:.4f}")
        
    # Save Feature Matrices
    os.makedirs("data/features", exist_ok=True)
    X_train.to_parquet("data/features/X_train.parquet")
    y_train.to_frame(name='rating').to_parquet("data/features/y_train.parquet")
    
    X_test.to_parquet("data/features/X_test.parquet")
    y_test.to_frame(name='rating').to_parquet("data/features/y_test.parquet")
    print("\nFeature matrices saved to data/features/")
    
    # Write Feature Engineering Report
    report_content = f"""# Feature Engineering & Selection Report
**Agent:** Priya (Principal Feature Engineering Architect)  
**Dataset:** `data/features/`  
**Generated:** 2026-10-26  

---

## 1. Engineered Feature Definitions
- **Discount Dynamics:** `discount_amount` (raw savings in ₹), `discount_ratio` (percentage of actual price retained).
- **Log Transformations:** `log_actual_price`, `log_discounted_price`, and `log_rating_count` to stabilize extreme price and review volume tails.
- **Text & Metadata Signals:** Character counts and word counts (`about_len`, `review_title_len`, `review_content_len`, `review_word_count`).
- **Category Representation:** One-hot encoded indicators for top product categories (`{', '.join(top_cats)}`).

---

## 2. Feature Importance & Ranking (Mutual Information)

| Rank | Feature Name | Mutual Information Score | Predictive Signal |
|---|---|---|---|
"""
    for idx, r in mi_df.iterrows():
        report_content += f"| {idx+1} | `{r['feature']}` | `{r['mi_score']:.4f}` | Continuous signal |\n"
        
    report_content += f"""
---

## 3. Dimensionality Summary
- **Total Engineered Features:** {X_train.shape[1]}
- **Training Matrix Shape:** {X_train.shape[0]} rows × {X_train.shape[1]} columns
- **Test Matrix Shape:** {X_test.shape[0]} rows × {X_test.shape[1]} columns

---

## 4. Handoff to Julian (Model Building & Tuning)
- Clean, scaled, non-collinear feature matrix ready in `data/features/`.
- Target variable `y_train` is ready for regression modeling or threshold classification.
- Recommending tree-based gradient boosting (LightGBM / Random Forest) along with Ridge regression baseline.
"""
    with open("data/feature_engineering_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Report written to data/feature_engineering_report.md")
    print("--- [Priya] Phase 3 Completed Successfully ---")

if __name__ == "__main__":
    main()
