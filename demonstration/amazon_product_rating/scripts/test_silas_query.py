import duckdb

def main():
    print("--- [Silas] Executing High-Performance DuckDB Query on Raw Data ---")
    con = duckdb.connect()
    
    query = """
    WITH raw_data AS (
        SELECT 
            product_id,
            product_name,
            SPLIT_PART(category, '|', 1) AS primary_category,
            CAST(REPLACE(REPLACE(discounted_price, '₹', ''), ',', '') AS DOUBLE) AS discounted_price_num,
            CAST(REPLACE(REPLACE(actual_price, '₹', ''), ',', '') AS DOUBLE) AS actual_price_num,
            CAST(NULLIF(REPLACE(rating, '|', ''), '') AS DOUBLE) AS rating_num,
            CAST(REPLACE(rating_count, ',', '') AS BIGINT) AS rating_count_num
        FROM read_csv_auto('data/amazon.csv')
    ),
    category_summary AS (
        SELECT 
            primary_category,
            COUNT(*) AS total_items,
            ROUND(AVG(actual_price_num), 2) AS avg_actual_price,
            ROUND(AVG(discounted_price_num), 2) AS avg_discounted_price,
            ROUND(AVG(rating_num), 2) AS avg_consumer_rating,
            SUM(rating_count_num) AS total_reviews_volume
        FROM raw_data
        WHERE rating_num IS NOT NULL
        GROUP BY primary_category
        ORDER BY total_items DESC
    )
    SELECT * FROM category_summary;
    """
    
    df = con.execute(query).df()
    print("\n[Silas Query Output - Extracted Category Summary]")
    print(df.to_string(index=False))
    
if __name__ == "__main__":
    main()
