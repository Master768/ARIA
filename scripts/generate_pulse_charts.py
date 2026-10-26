"""
Maya: Generate Exploratory Visualizations for Pulse DB User Performance
"""
import os
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

os.makedirs("reports/assets", exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

con = duckdb.connect()

# Load joined daily logs & predictions
query = """
SELECT 
    d.userId,
    u.name,
    d.sleepHours,
    d.studyHours,
    d.screenTimeHours,
    d.exerciseMins,
    d.moodScore,
    d.stressLevel,
    p.productivityScore,
    p.burnoutRisk
FROM read_parquet('data/raw/pulse_dailylogs.parquet') d
JOIN read_parquet('data/raw/pulse_predictions.parquet') p 
    ON d._id = p.logId OR (d.userId = p.userId AND d.date = p.date)
JOIN read_parquet('data/raw/pulse_users.parquet') u
    ON d.userId = u._id
"""
df = con.execute(query).df()

if len(df) == 0:
    # Fallback join on userId and approximate match or just use dailylogs + predictions directly
    query = """
    SELECT 
        u.name,
        d.sleepHours,
        d.studyHours,
        d.screenTimeHours,
        d.exerciseMins,
        d.moodScore,
        d.stressLevel,
        p.productivityScore,
        p.burnoutRisk
    FROM read_parquet('data/raw/pulse_dailylogs.parquet') d
    JOIN read_parquet('data/raw/pulse_predictions.parquet') p ON d.userId = p.userId
    JOIN read_parquet('data/raw/pulse_users.parquet') u ON d.userId = u._id
    """
    df = con.execute(query).df()

# 1. User Ranking Bar Chart (Active Users by Avg Productivity - Anonymized)
user_summary = pd.read_csv("data/user_performance_summary.csv")
active_users = user_summary[user_summary['predictions_count'] > 0].sort_values('avg_productivity', ascending=False).reset_index(drop=True)

# Generate anonymized cohort labels for public release
active_users['cohort_id'] = [f"Participant {i+1:02d}" for i in range(len(active_users))]

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
colors = ['#2E7D32' if r == 'Low' else '#F57C00' if r == 'Medium' else '#D32F2F' for r in active_users['burnout_risk'].head(15)]
bars = ax.barh(active_users['cohort_id'].head(15)[::-1], active_users['avg_productivity'].head(15)[::-1], color=colors[::-1], edgecolor='none', height=0.65)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 1, bar.get_y() + bar.get_height()/2, f'{w:.1f}', ha='left', va='center', fontsize=9, fontweight='bold', color='#1A365D')

ax.set_xlim(0, 110)
ax.set_title('Cohort Benchmark: Productivity Score & Burnout Risk (Sample Audience)', fontsize=12, fontweight='bold', pad=15, color='#1A365D')
ax.set_xlabel('Productivity Score (0 - 100)', fontsize=10, fontweight='bold', color='#2D3748')
plt.tight_layout()
plt.savefig('reports/assets/pulse_user_productivity_ranking.png', dpi=300)
plt.close()

# 2. Lifestyle vs Productivity Scatter & Correlation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

# Sleep vs Productivity
sns.regplot(data=df, x='sleepHours', y='productivityScore', ax=ax1, scatter_kws={'alpha': 0.6, 'color': '#2B6CB0'}, line_kws={'color': '#C53030', 'linewidth': 2})
ax1.set_title('Sleep Duration vs. Productivity Score', fontsize=11, fontweight='bold', color='#1A365D')
ax1.set_xlabel('Sleep Hours', fontsize=10)
ax1.set_ylabel('Productivity Score', fontsize=10)

# Screen Time vs Productivity
sns.regplot(data=df, x='screenTimeHours', y='productivityScore', ax=ax2, scatter_kws={'alpha': 0.6, 'color': '#D69E2E'}, line_kws={'color': '#805AD5', 'linewidth': 2})
ax2.set_title('Screen Time vs. Productivity Score', fontsize=11, fontweight='bold', color='#1A365D')
ax2.set_xlabel('Screen Time Hours', fontsize=10)
ax2.set_ylabel('Productivity Score', fontsize=10)

plt.tight_layout()
plt.savefig('reports/assets/pulse_lifestyle_vs_productivity.png', dpi=300)
plt.close()

print("Charts successfully saved to reports/assets/")
