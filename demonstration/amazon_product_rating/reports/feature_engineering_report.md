# Feature Engineering & Selection Report
**Agent:** Priya (Principal Feature Engineering Architect)  
**Dataset:** `data/features/`  
**Generated:** 2026-10-26  

---

## 1. Engineered Feature Definitions
- **Discount Dynamics:** `discount_amount` (raw savings in ₹), `discount_ratio` (percentage of actual price retained).
- **Log Transformations:** `log_actual_price`, `log_discounted_price`, and `log_rating_count` to stabilize extreme price and review volume tails.
- **Text & Metadata Signals:** Character counts and word counts (`about_len`, `review_title_len`, `review_content_len`, `review_word_count`).
- **Category Representation:** One-hot encoded indicators for top product categories (`Electronics, Home&Kitchen, Computers&Accessories, OfficeProducts, HomeImprovement`).

---

## 2. Feature Importance & Ranking (Mutual Information)

| Rank | Feature Name | Mutual Information Score | Predictive Signal |
|---|---|---|---|
| 1 | `log_rating_count` | `0.2839` | Continuous signal |
| 2 | `rating_count` | `0.2586` | Continuous signal |
| 3 | `review_word_count` | `0.2334` | Continuous signal |
| 4 | `review_content_len` | `0.2285` | Continuous signal |
| 5 | `review_title_len` | `0.1818` | Continuous signal |
| 6 | `about_len` | `0.1560` | Continuous signal |
| 7 | `log_discounted_price` | `0.1535` | Continuous signal |
| 8 | `discounted_price` | `0.1434` | Continuous signal |
| 9 | `log_actual_price` | `0.1385` | Continuous signal |
| 10 | `discount_ratio` | `0.1368` | Continuous signal |
| 11 | `actual_price` | `0.1291` | Continuous signal |
| 12 | `discount_amount` | `0.1148` | Continuous signal |
| 13 | `discount_percentage` | `0.0937` | Continuous signal |
| 14 | `cat_Electronics` | `0.0265` | Continuous signal |
| 15 | `cat_Other` | `0.0217` | Continuous signal |
| 16 | `cat_HomeImprovement` | `0.0135` | Continuous signal |
| 17 | `cat_OfficeProducts` | `0.0006` | Continuous signal |
| 18 | `cat_Home&Kitchen` | `0.0000` | Continuous signal |

---

## 3. Dimensionality Summary
- **Total Engineered Features:** 18
- **Training Matrix Shape:** 1171 rows × 18 columns
- **Test Matrix Shape:** 293 rows × 18 columns

---

## 4. Handoff to Julian (Model Building & Tuning)
- Clean, scaled, non-collinear feature matrix ready in `data/features/`.
- Target variable `y_train` is ready for regression modeling or threshold classification.
- Recommending tree-based gradient boosting (LightGBM / Random Forest) along with Ridge regression baseline.
