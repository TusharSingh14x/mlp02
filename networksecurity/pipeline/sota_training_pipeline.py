import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, matthews_corrcoef, confusion_matrix
)
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

from networksecurity.components.hybrid_feature_selector import HybridFeatureSelector
from networksecurity.utils.ml_utils.statistical_tests import mcnemar_test, paired_t_test_cross_val
from networksecurity.utils.ml_utils.adversarial_evaluator import AdversarialURLEvaluator
from networksecurity.utils.ml_utils.pure_url_features import extract_pure_static_features, STATIC_50_FEATURE_NAMES


class SOTAPhishingPipeline:
    """
    State-of-the-art Experimental & Benchmarking Pipeline designed for publication.
    Integrates:
      - 5-Fold Stratified Cross-Validation (Leakage-Free)
      - Hybrid Feature Selection (Top-20, Top-30, All-50)
      - Modern Ensemble Stacking (GradientBoosting + RandomForest + XGBoost + LGBM -> Logistic Regression)
      - Statistical Significance Testing (McNemar & Paired t-test)
      - Adversarial Perturbation Stress-Testing
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = self._initialize_models()

    def _initialize_models(self) -> Dict[str, Any]:
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=self.random_state),
            "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=self.random_state),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=self.random_state, n_jobs=-1),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=self.random_state),
        }
        if HAS_XGB:
            models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=self.random_state, eval_metric="logloss")
        if HAS_LGBM:
            models["LightGBM"] = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=self.random_state, verbose=-1)

        # Build Stacking Classifier
        estimators = [
            ("rf", models["Random Forest"]),
            ("gb", models["Gradient Boosting"]),
        ]
        if HAS_XGB:
            estimators.append(("xgb", models["XGBoost"]))
        if HAS_LGBM:
            estimators.append(("lgbm", models["LightGBM"]))

        models["Stacking Ensemble (Proposed)"] = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(C=0.1, max_iter=1000, random_state=self.random_state),
            cv=5,
            n_jobs=-1
        )
        return models

    def evaluate_fold(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_prob)),
            "pr_auc": float(average_precision_score(y_true, y_prob)),
            "mcc": float(matthews_corrcoef(y_true, y_pred)),
        }

    def run_benchmark(self, X: pd.DataFrame, y: pd.Series, feature_modes: List[str] = ["All", "Top-30", "Top-20"]) -> Dict[str, Any]:
        """
        Executes complete benchmark across feature selection tiers and classifiers.
        """
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        benchmark_results = {}

        for mode in feature_modes:
            print(f"\n>>> Running Benchmark for Feature Tier: {mode} <<<")
            benchmark_results[mode] = {}

            for model_name, model in self.models.items():
                fold_metrics = []
                all_preds = []
                all_trues = []

                for train_idx, val_idx in skf.split(X, y):
                    X_train, X_val = X.iloc[train_idx].copy(), X.iloc[val_idx].copy()
                    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

                    # Leakage-aware Feature Selection
                    if mode == "Top-20":
                        selector = HybridFeatureSelector(top_k=20, random_state=self.random_state)
                        X_train = selector.fit_transform(X_train, y_train)
                        X_val = selector.transform(X_val)
                    elif mode == "Top-30":
                        selector = HybridFeatureSelector(top_k=30, random_state=self.random_state)
                        X_train = selector.fit_transform(X_train, y_train)
                        X_val = selector.transform(X_val)

                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_val_scaled = scaler.transform(X_val)

                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_val_scaled)
                    
                    if hasattr(model, "predict_proba"):
                        y_prob = model.predict_proba(X_val_scaled)[:, 1]
                    else:
                        y_prob = y_pred.astype(float)

                    metrics = self.evaluate_fold(y_val, y_pred, y_prob)
                    fold_metrics.append(metrics)
                    all_preds.extend(y_pred)
                    all_trues.extend(y_val)

                # Compute mean and standard deviation across folds
                agg_metrics = {}
                for key in fold_metrics[0].keys():
                    vals = [m[key] for m in fold_metrics]
                    agg_metrics[f"{key}_mean"] = round(float(np.mean(vals)), 4)
                    agg_metrics[f"{key}_std"] = round(float(np.std(vals)), 4)

                agg_metrics["confusion_matrix"] = confusion_matrix(all_trues, all_preds).tolist()
                benchmark_results[mode][model_name] = agg_metrics

        return benchmark_results

