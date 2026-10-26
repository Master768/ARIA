"""
Silas & Maya: User Performance and Behavioral Analysis
Joins users, predictions, and dailylogs to profile user performance.
"""
import duckdb
import pandas as pd

def main():
    con = duckdb.connect()

    query = """
    WITH log_stats AS (
        SELECT 
            userId,
            COUNT(*) AS total_logs,
            ROUND(AVG(sleepHours), 2) AS avg_sleep_hrs,
            ROUND(AVG(studyHours), 2) AS avg_study_hrs,
            ROUND(AVG(screenTimeHours), 2) AS avg_screen_hrs,
            ROUND(AVG(exerciseMins), 1) AS avg_exercise_mins,
            ROUND(AVG(moodScore), 2) AS avg_mood,
            ROUND(AVG(stressLevel), 2) AS avg_stress
        FROM read_parquet('data/raw/pulse_dailylogs.parquet')
        GROUP BY userId
    ),
    pred_stats AS (
        SELECT 
            userId,
            COUNT(*) AS total_predictions,
            ROUND(AVG(productivityScore), 1) AS avg_productivity,
            MIN(productivityScore) AS min_productivity,
            MAX(productivityScore) AS max_productivity,
            MODE(burnoutRisk) AS common_burnout_risk
        FROM read_parquet('data/raw/pulse_predictions.parquet')
        GROUP BY userId
    )
    SELECT 
        u.name,
        u.email,
        COALESCE(u.persona, 'Unassigned') AS persona,
        COALESCE(u.streakCount, 0) AS streak,
        COALESCE(l.total_logs, 0) AS logs_count,
        COALESCE(p.total_predictions, 0) AS predictions_count,
        p.avg_productivity,
        p.min_productivity,
        p.max_productivity,
        COALESCE(p.common_burnout_risk, 'N/A') AS burnout_risk,
        l.avg_sleep_hrs,
        l.avg_study_hrs,
        l.avg_screen_hrs,
        l.avg_stress,
        l.avg_mood
    FROM read_parquet('data/raw/pulse_users.parquet') u
    LEFT JOIN pred_stats p ON u._id = p.userId
    LEFT JOIN log_stats l ON u._id = l.userId
    ORDER BY 
        CASE WHEN p.avg_productivity IS NULL THEN 1 ELSE 0 END,
        p.avg_productivity DESC,
        u.name ASC
    """
    
    df = con.execute(query).df()
    print("--- User Performance Summary Table ---")
    print(df.to_string(index=False))

    # Also save to CSV and Markdown
    df.to_csv("data/user_performance_summary.csv", index=False)
    
    # Save a detailed report
    active_users = df[df['predictions_count'] > 0]
    inactive_users = df[df['predictions_count'] == 0]
    
    print(f"\nTotal Registered Users: {len(df)}")
    print(f"Users with Active Predictions/Logs: {len(active_users)}")
    print(f"Users without Activity Logs: {len(inactive_users)}")

if __name__ == "__main__":
    main()
