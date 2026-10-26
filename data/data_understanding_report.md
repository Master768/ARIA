# Data Understanding & Exploration Report
**Agent:** Maya (Lead Exploratory Data Scientist)  
**Dataset:** `data/amazon.csv`  
**Generated:** 2026-10-26  

---

## 1. Executive Summary
- **Dataset Dimensions:** 1,465 rows × 16 columns.
- **Target Variable Identified:** `rating` (Continuous scale 1.0 – 5.0).
- **Target Distribution:** Mean = `4.10`, Median = `4.10`, Std = `0.29`, Skewness = `-1.24` (Left-skewed towards high ratings).
- **Duplicate Records:** 0 exact duplicate rows.

---

## 2. Data Dictionary & Schema Profile

| Column | Data Type | Null Count | Null % | Unique Values | Sample Value |
|---|---|---|---|---|---|
| `product_id` | `object` | 0 | 0.0% | 1,351 | `B07JW9H4J1` |
| `product_name` | `object` | 0 | 0.0% | 1,337 | `Wayona Nylon Braided USB to Lightning Fa` |
| `category` | `object` | 0 | 0.0% | 211 | `Computers&Accessories|Accessories&Periph` |
| `discounted_price` | `object` | 0 | 0.0% | 550 | `₹399` |
| `actual_price` | `object` | 0 | 0.0% | 449 | `₹1,099` |
| `discount_percentage` | `object` | 0 | 0.0% | 92 | `64%` |
| `rating` | `object` | 0 | 0.0% | 28 | `4.2` |
| `rating_count` | `object` | 2 | 0.14% | 1,143 | `24,269` |
| `about_product` | `object` | 0 | 0.0% | 1,293 | `High Compatibility : Compatible With iPh` |
| `user_id` | `object` | 0 | 0.0% | 1,194 | `AG3D6O4STAQKAY2UVGEUV46KN35Q,AHMY5CWJMMK` |
| `user_name` | `object` | 0 | 0.0% | 1,194 | `Manav,Adarsh gupta,Sundeep,S.Sayeed Ahme` |
| `review_id` | `object` | 0 | 0.0% | 1,194 | `R3HXWT0LRP0NMF,R2AJM3LFTLZHFO,R6AQJGUP6P` |
| `review_title` | `object` | 0 | 0.0% | 1,194 | `Satisfied,Charging is really fast,Value ` |
| `review_content` | `object` | 0 | 0.0% | 1,212 | `Looks durable Charging is fine tooNo com` |
| `img_link` | `object` | 0 | 0.0% | 1,412 | `https://m.media-amazon.com/images/W/WEBP` |
| `product_link` | `object` | 0 | 0.0% | 1,465 | `https://www.amazon.in/Wayona-Braided-WN3` |

---

## 3. Data Quality & Preprocessing Red Flags
1. **Currency & Formatting Pollution:** `discounted_price` and `actual_price` contain Indian Rupee currency symbols (`₹`) and comma thousand separators (e.g. `₹1,099`). They must be converted to float.
2. **Percentage Formatting:** `discount_percentage` is stored as text with `%` signs (e.g. `50%`).
3. **Invalid Characters in Numeric Fields:** The `rating` column contains non-numeric character anomalies (e.g. `|` pipe characters in rogue records).
4. **Rating Count Formatting:** `rating_count` contains commas as thousands separators (e.g. `24,269`) and has 2 missing values.
5. **Hierarchical Categorical Strings:** `category` uses pipe-separated taxomomies (`Electronics|Cables|...`). Primary categories need parsing.

---

## 4. Visual Evidence
![Rating Distribution](assets/eda_rating_distribution.png)
*Figure 1: Distribution of Amazon Product Ratings (Mean: 4.10, Median: 4.10).*

![Top Categories](assets/eda_top_categories.png)
*Figure 2: Distribution of Top Categories in the Dataset.*

---

## 5. Handoff to Leo (Data Cleaning & Preprocessing)
- **Priority 1:** Strip currency symbols and parse `actual_price`, `discounted_price`, and `discount_percentage` to `float32`.
- **Priority 2:** Clean `rating` column into numeric, removing rogue rows with non-numeric values.
- **Priority 3:** Impute missing `rating_count` with median after numeric casting.
- **Priority 4:** Extract `primary_category` from `category`.
