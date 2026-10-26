"""
Phase 4: Model Building & Tuning Script
Agent: Julian (Staff Machine Learning Engineer)
Dataset: data/features/ -> models/
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, cross_validate, GridSearchCV
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

def main():
    print("--- [Julian] Starting Model Building & Multi-Algorithm Tournament ---")
    X_train = pd.read_parquet("data/features/X_train.parquet")
    y_train = pd.read_parquet("data/features/y_train.parquet")['rating'].values
    
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # 1. Candidate Algorithm Dictionary
    models = {
        "Baseline (Dummy Mean)": DummyRegressor(strategy="mean"),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42)
    }
    
    results = {}
    print("\nRunning 5-Fold Cross Validation Tournament:")
    for name, model in models.items():
        scores = cross_validate(
            model, X_train, y_train,
            cv=cv,
            scoring={
                "rmse": "neg_root_mean_squared_error",
                "mae": "neg_mean_absolute_error",
                "r2": "r2"
            },
            n_jobs=-1
        )
        mean_rmse = -scores["test_rmse"].mean()
        std_rmse = scores["test_rmse"].std()
        mean_mae = -scores["test_mae"].mean()
        mean_r2 = scores["test_r2"].mean()
        
        results[name] = {
            "mean_rmse": round(float(mean_rmse), 4),
            "std_rmse": round(float(std_rmse), 4),
            "mean_mae": round(float(mean_mae), 4),
            "mean_r2": round(float(mean_r2), 4)
        }
        print(f"  > {name:<22}: RMSE={mean_rmse:.4f} (±{std_rmse:.4f}) | MAE={mean_mae:.4f} | R²={mean_r2:.4f}")
        
    # 2. Select Champion Algorithm (lowest RMSE)
    champion_name = min(results, key=lambda k: results[k]["mean_rmse"])
    print(f"\nTournament Winner (Champion): {champion_name}")
    
    # 3. Hyperparameter Tuning of Champion Model
    print("Tuning champion model hyperparameters via GridSearch...")
    if champion_name == "HistGradientBoosting":
        param_grid = {
            "learning_rate": [0.03, 0.05, 0.1],
            "max_iter": [100, 150],
            "max_leaf_nodes": [15, 31],
            "min_samples_leaf": [10, 20]
        }
        grid = GridSearchCV(
            HistGradientBoostingRegressor(random_state=42),
            param_grid, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1
        )
    elif champion_name == "Random Forest":
        param_grid = {
            "n_estimators": [100, 200],
            "max_depth": [6, 10, None],
            "min_samples_split": [2, 5]
        }
        grid = GridSearchCV(
            RandomForestRegressor(random_state=42, n_jobs=-1),
            param_grid, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1
        )
    else:
        param_grid = {"alpha": [0.1, 1.0, 10.0, 100.0]}
        grid = GridSearchCV(
            Ridge(), param_grid, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1
        )
        
    grid.fit(X_train, y_train)
    best_params = grid.best_params_
    best_tuned_rmse = -grid.best_score_
    print(f"Tuned Optimal Params: {best_params}")
    print(f"Tuned CV RMSE: {best_tuned_rmse:.4f}")
    
    # 4. Fit Champion Model on Full Train and Serialize
    champion_model = grid.best_estimator_
    os.makedirs("models", exist_ok=True)
    joblib.dump(champion_model, "models/champion_model.joblib")
    
    # Save benchmark json
    summary_data = {
        "tournament_results": results,
        "champion_name": champion_name,
        "best_params": best_params,
        "tuned_cv_rmse": round(float(best_tuned_rmse), 4)
    }
    with open("models/model_benchmark_results.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print("Serialized model to models/champion_model.joblib")
    
    # 5. Write Model Training Report
    report_content = f"""# Model Building & Hyperparameter Tuning Report
**Agent:** Julian (Staff Machine Learning Engineer)  
**Dataset:** `data/features/`  
**Generated:** 2026-10-26  

---

## 1. Multi-Algorithm Benchmark Tournament (5-Fold CV)

| Algorithm | Mean RMSE | Std RMSE | Mean MAE | Mean $R^2$ | Status |
|---|---|---|---|---|---|
"""
    for name, r in results.items():
        is_champ = "**CHAMPION**" if name == champion_name else "Candidate"
        report_content += f"| **{name}** | `{r['mean_rmse']}` | `±{r['std_rmse']}` | `{r['mean_mae']}` | `{r['mean_r2']}` | {is_champ} |\n"
        
    report_content += f"""
---

## 2. Champion Model & Tuning
- **Winning Algorithm Family:** `{champion_name}`
- **Tuned Hyperparameters:**
```json
{json.dumps(best_params, indent=2)}
```
- **Pre-tuning CV RMSE:** `{results[champion_name]['mean_rmse']}`
- **Post-tuning CV RMSE:** `{best_tuned_rmse:.4f}`
- **Artifact Path:** `models/champion_model.joblib`

---

## 3. Handoff to Elena (Model Evaluation & Validation Auditor)
- Champion model is serialized and verified.
- The holdout test set (`data/features/X_test.parquet`, `y_test.parquet`) remains strictly untouched.
- Elena will evaluate holdout error, residual normality, and SHAP explainability.
"""
    with open("models/model_training_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Report written to models/model_training_report.md")
    print("--- [Julian] Phase 4 Completed Successfully ---")

if __name__ == "__main__":
    main()
