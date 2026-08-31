# Analysis Report: Clean the dataset by handling missing values, duplicate records, and inconsistent player statistics. Compute summary statistics for all numerical columns. Identify the top 10 players whose tournament_rating is significantly higher than their player_rating despite playing fewer than the median tournament minutes. Explain which offensive, defensive, and physical metrics contributed most to this overperformance using correlation analysis, feature importance ranking, and comparative statistics against players in the same position in fifa dataset

**Date:** 2026-08-08T09:40:47.098227+00:00
**Status:** COMPLETED

## Executive Summary
# Executive Analytics Summary

**Query:** 'Clean the dataset by handling missing values, duplicate records, and inconsistent player statistics. Compute summary statistics for all numerical columns. Identify the top 10 players whose tournament_rating is significantly higher than their player_rating despite playing fewer than the median tournament minutes. Explain which offensive, defensive, and physical metrics contributed most to this overperformance using correlation analysis, feature importance ranking, and comparative statistics against players in the same position in fifa dataset'

### 📊 Computed Key Numeric Statistics (Native Engine):
- **age**: Mean=26.30, Std=4.07, Median=26.00
- **jersey_number**: Mean=13.50, Std=7.50, Median=13.50
- **height_cm**: Mean=181.65, Std=6.28, Median=182.00
- **weight_kg**: Mean=75.75, Std=3.95, Median=76.00
- **market_value_eur**: Mean=20084451.76, Std=27188660.40, Median=10271107.00

### 🔍 Analysis Node `node_1` Findings:
Loaded dataset with shape: (54600, 75)
Rows after duplicate removal: 54600

Summary statistics (numeric columns):
                    count          mean  ...         75%           max
age               54600.0  2.629613e+01  ...        29.0  3.849904e+01
jersey_number     54600.0  1.350000e+01  ...        20.0  2.600000e+01
height_cm         54600.0  1.816543e+02  ...       186.0  2.000000e+02
weight_kg         54600.0  7.575485e+01  ...        78.0  8.700000e+01
market_value_eur  54600.0  1.916916e+07  ...  23420128.0  1.016504e+08

[5 rows x 8 columns]

Median tournament minutes: 268.0

Top 10 over‑performing players:
            player_name player_id  ... total_minutes_tournament  rating_diff
7985   Youssef Laidouni    P01149  ...                    242.0          1.1
82         Denzel Malen    P00140  ...                    248.0          1.0
3484   Harry Bellingham    P00079  ...                    189.0          1.0
11421       Frenkie Ake    P00143  ...                    194.0          1.0
14545        Erick Mena    P00554  ...                    155.0          1.0
17664         Joel Soto    P00742  ...                    139.0          1.0
42432     Frenkie Gakpo    P00131  ...                    201.0          1.0
52034      Youri Chadli    P00164  ...                    264.0          1.0
52586   Mohannad Majeed    P01009  ...                    174.0          1.0
40568    Edinson Torres    P00594  ...                    245.0          1.0

[10 rows x 7 columns]

Top positive correlations with tournament_rating:
tournament_rating      1.000000
player_rating          0.997337
performance_score      0.993943
top_speed_kmh          0.976900
minutes_played         0.835092
distance_covered_km    0.835002
sprint_distance_km     0.818502
accelerations          0.796369
decelerations          0.792289
total_passes           0.745776
Name: tournament_rating, dtype: float64

Top negative correlations with tournament_rating:
clutch_performance_score    0.012749
goals_team                  0.008814
yellow_cards                0.003166
red_cards                  -0.006229
goals_opponent             -0.007414
defensive_contribution     -0.015650
penalty_saves              -0.032444
age                        -0.038970
weight_kg                  -0.047990
height_cm                  -0.079246
Name: tournament_rating, dtype: float64

Top 10 feature importances:
top_speed_kmh               0.222021
minutes_played              0.217005
performance_score           0.190865
sprint_distance_km          0.188019
distance_covered_km         0.173667
consistency_score           0.000503
market_value_eur            0.000490
clutch_performance_score    0.000482
pressure_resistance         0.000481
stamina_score               0.000427
dtype: float64

Top 3 players – differences from position averages (top 5 metrics):

Player: Youssef Laidouni (Position: Defender)
pressure_resistance         27.057481
creativity_score            12.681720
offensive_contribution       7.137111
age                          4.333228
total_minutes_tournament     1.871058
dtype: float64

Player: Denzel Malen (Position: Defender)
market_value_eur     4.104792e+06
minutes_played       3.450762e+01
performance_score    2.233976e+01
total_passes         1.989055e+01
stamina_score        1.682915e+01
dtype: float64

Player: Harry Bellingham (Position: Goalkeeper)
market_value_eur          3.964563e+06
minutes_played            6.444667e+01
performance_score         5.232359e+01
defensive_contribution    2.973949e+01
decelerations             2.575651e+01
dtype: float64


### 🔍 Analysis Node `node_2` Findings:
Initial shape: (54600, 75)
Columns: ['player_id', 'player_name', 'age', 'nationality', 'team', 'jersey_number', 'position', 'height_cm', 'weight_kg', 'preferred_foot', 'club_name', 'market_value_eur', 'match_id', 'match_date', 'stadium', 'city', 'opponent_team', 'tournament_stage', 'match_result', 'goals_team', 'goals_opponent', 'minutes_played', 'goals', 'assists', 'shots', 'shots_on_target', 'expected_goals_xg', 'expected_assists_xa', 'key_passes', 'successful_passes', 'total_passes', 'pass_accuracy', 'dribbles_attempted', 'successful_dribbles', 'crosses', 'successful_crosses', 'tackles', 'interceptions', 'clearances', 'blocks', 'aerial_duels_won', 'aerial_duels_lost', 'recoveries', 'defensive_actions', 'fouls_committed', 'fouls_suffered', 'yellow_cards', 'red_cards', 'offsides', 'saves', 'save_percentage', 'punches', 'clean_sheet', 'goals_conceded', 'penalty_saves', 'distance_covered_km', 'sprint_distance_km', 'top_speed_kmh', 'accelerations', 'decelerations', 'stamina_score', 'player_rating', 'performance_score', 'offensive_contribution', 'defensive_contribution', 'possession_impact', 'pressure_resistance', 'creativity_score', 'consistency_score', 'clutch_performance_score', 'total_goals_tournament', 'total_assists_tournament', 'total_minutes_tournament', 'player_of_match_awards', 'tournament_rating']
Numeric columns: ['age', 'jersey_number', 'height_cm', 'weight_kg', 'market_value_eur', 'goals_team', 'goals_opponent', 'minutes_played', 'goals', 'assists', 'shots', 'shots_on_target', 'expected_goals_xg', 'expected_assists_xa', 'key_passes', 'successful_passes', 'total_passes', 'pass_accuracy', 'dribbles_attempted', 'successful_dribbles', 'crosses', 'successful_crosses', 'tackles', 'interceptions', 'clearances', 'blocks', 'aerial_duels_won', 'aerial_duels_lost', 'recoveries', 'defensive_actions', 'fouls_committed', 'fouls_suffered', 'yellow_cards', 'red_cards', 'offsides', 'saves', 'save_percentage', 'punches', 'clean_sheet', 'goals_conceded', 'penalty_saves', 'distance_covered_km', 'sprint_distance_km', 'top_speed_kmh', 'accelerations', 'decelerations', 'stamina_score', 'player_rating', 'performance_score', 'offensive_contribution', 'defensive_contribution', 'possession_impact', 'pressure_resistance', 'creativity_score', 'consistency_score', 'clutch_performance_score', 'total_goals_tournament', 'total_assists_tournament', 'total_minutes_tournament', 'player_of_match_awards', 'tournament_rating']
Dropped duplicates: 0
Summary statistics:
                    count          mean  ...         75%         max
age               54600.0  2.629579e+01  ...        29.0        38.0
jersey_number     54600.0  1.350000e+01  ...        20.0        26.0
height_cm         54600.0  1.816545e+02  ...       186.0       199.5
weight_kg         54600.0  7.575597e+01  ...        78.0        85.5
market_value_eur  54600.0  1.651869e+07  ...  23420128.0  51883153.0

[5 rows x 8 columns]
Median tournament minutes: 268.0
Top 10 players:
      player_id       player_name  ... total_minutes_tournament  rating_diff
7985     P01149  Youssef Laidouni  ...                    242.0          1.1
52034    P00164      Youri Chadli  ...                    264.0          1.0
17664    P00742         Joel Soto  ...                    139.0          1.0
11421    P00143       Frenkie Ake  ...                    194.0          1.0
82       P00140      Denzel Malen  ...                    248.0          1.0
42432    P00131     Frenkie Gakpo  ...                    201.0          1.0
14545    P00554        Erick Mena  ...                    155.0          1.0
3484     P00079  Harry Bellingham  ...                    189.0          1.0
52586    P01009   Mohannad Majeed  ...                    174.0          1.0
40568    P00594    Edinson Torres  ...                    245.0          1.0

[10 rows x 7 columns]
Top positive correlations with tournament_rating:
tournament_rating      1.000000
player_rating          0.997337
performance_score      0.993943
top_speed_kmh          0.976900
minutes_played         0.835092
distance_covered_km    0.835002
sprint_distance_km     0.818468
accelerations          0.796357
decelerations          0.792261
total_passes           0.748408
Name: tournament_rating, dtype: float64
Top negative correlations:
yellow_cards             NaN
red_cards                NaN
offsides                 NaN
saves                    NaN
save_percentage          NaN
punches                  NaN
clean_sheet              NaN
goals_conceded           NaN
penalty_saves            NaN
player_of_match_awards   NaN
Name: tournament_rating, dtype: float64
RandomForest R2 on test set: 0.9945387977125482
Top 10 feature importances:
player_rating               0.199847
performance_score           0.197763
sprint_distance_km          0.168688
distance_covered_km         0.163946
top_speed_kmh               0.135118
minutes_played              0.130193
total_minutes_tournament    0.000269
clutch_performance_score    0.000265
stamina_score               0.000246
creativity_score            0.000232
dtype: float64
Comparative stats for top players vs position averages:
P01149 offensive_contribution    32.262889
defensive_contribution    67.331619
stamina_score             82.176661
distance_covered_km        3.993116
sprint_distance_km         0.463116
top_speed_kmh             19.749418
dtype: float64
P00164 offensive_contribution    32.262889
defensive_contribution    67.331619
stamina_score             82.176661
distance_covered_km        3.993116
sprint_distance_km         0.463116
top_speed_kmh             19.749418
dtype: float64
P00742 offensive_contribution    56.093167
defensive_contribution    50.997518
stamina_score             82.369179
distance_covered_km        4.498935
sprint_distance_km         0.517702
top_speed_kmh             19.862970
dtype: float64
P00143 offensive_contribution    56.093167
defensive_contribution    50.997518
stamina_score             82.369179
distance_covered_km        4.498935
sprint_distance_km         0.517702
top_speed_kmh             19.862970
dtype: float64
P00140 offensive_contribution    32.262889
defensive_contribution    67.331619
stamina_score             82.176661
distance_covered_km        3.993116
sprint_distance_km         0.463116
top_speed_kmh             19.749418
dtype: float64
P00131 offensive_contribution    10.091492
defensive_contribution    69.260508
stamina_score             78.854952
distance_covered_km        2.410810
sprint_distance_km         0.276794
top_speed_kmh              9.675905
dtype: float64
P00554 offensive_contribution    32.262889
defensive_contribution    67.331619
stamina_score             82.176661
distance_covered_km        3.993116
sprint_distance_km         0.463116
top_speed_kmh             19.749418
dtype: float64
P00079 offensive_contribution    10.091492
defensive_contribution    69.260508
stamina_score             78.854952
distance_covered_km        2.410810
sprint_distance_km         0.276794
top_speed_kmh              9.675905
dtype: float64
P01009 offensive_contribution    65.541119
defensive_contribution    24.888381
stamina_score             82.379270
distance_covered_km        4.124524
sprint_distance_km         0.480270
top_speed_kmh             19.851714
dtype: float64
P00594 offensive_contribution    65.541119
defensive_contribution    24.888381
stamina_score             82.379270
distance_covered_km        4.124524
sprint_distance_km         0.480270
top_speed_kmh             19.851714
dtype: float64


### 🔍 Analysis Node `node_3` Findings:
TimeoutExpired: Code execution exceeded 120 seconds limit.

### 🔍 Analysis Node `node_4` Findings:
TimeoutExpired: Code execution exceeded 120 seconds limit.

### 🔍 Analysis Node `node_5` Findings:
Report sections compiled



## Detailed Findings