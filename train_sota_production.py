import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

from networksecurity.components.hybrid_feature_selector import HybridFeatureSelector

def main():
    print("[*] Training Production SOTA Stacking Ensemble...")
    data_path = "Network_Data/phisingData.csv"
    df = pd.read_csv(data_path)
    X = df.drop(columns=["Result"])
    y = df["Result"].map({-1: 0, 1: 1})

    print(f"[*] Loaded dataset: {X.shape[0]} rows, {X.shape[1]} raw features.")
    
    # 1. Fit Hybrid Feature Selector (Top-30)
    print("[*] Fitting Hybrid Feature Selector (Mutual Information + Chi2 + TreeSHAP)...")
    selector = HybridFeatureSelector(top_k=30, random_state=42)
    X_selected = selector.fit_transform(X, y)
    selected_features = selector.selected_features_
    print(f"[+] Selected Top-30 Features: {selected_features}")

    # 2. Build Stacking Ensemble
    estimators = [
        ("rf", RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)),
        ("gb", GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)),
        ("xgb", XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss")),
        ("lgbm", LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1))
    ]

    stacking_clf = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(C=0.1, max_iter=1000, random_state=42),
        cv=5,
        n_jobs=-1
    )

    print("[*] Fitting Stacking Ensemble...")
    stacking_clf.fit(X_selected, y)

    os.makedirs("final_model", exist_ok=True)
    joblib.dump(stacking_clf, "final_model/sota_stacking_model.pkl")
    joblib.dump(selector, "final_model/sota_feature_selector.pkl")
    with open("final_model/sota_top30_features.json", "w") as f:
        json.dump(selected_features, f, indent=2)

    print("[+] Successfully saved:")
    print("    - final_model/sota_stacking_model.pkl")
    print("    - final_model/sota_feature_selector.pkl")
    print("    - final_model/sota_top30_features.json")

if __name__ == "__main__":
    main()

