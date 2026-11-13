import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any
from sklearn.feature_selection import mutual_info_classif, chi2
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import shap


class HybridFeatureSelector:
    """
    Leakage-Aware Multi-Criteria Feature Selection Pipeline.
    Integrates:
      1. Information-Theoretic Relevance (Mutual Information)
      2. Statistical Association (Chi-Square)
      3. Tree-based Model Contribution (Random Forest Gini / TreeSHAP)
    """

    def __init__(
        self,
        top_k: int = 30,
        w_mi: float = 0.33,
        w_chi2: float = 0.33,
        w_shap: float = 0.34,
        shap_sample_size: int = 1500,
        random_state: int = 42,
    ):
        self.top_k = top_k
        self.w_mi = w_mi
        self.w_chi2 = w_chi2
        self.w_shap = w_shap
        self.shap_sample_size = shap_sample_size
        self.random_state = random_state
        self.selected_features_: List[str] = []
        self.feature_rankings_: pd.DataFrame = pd.DataFrame()

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "HybridFeatureSelector":
        """
        Fit feature selection strictly on the training partition.
        Prevents test-fold leakage.
        """
        feature_names = list(X.columns)
        n_features = len(feature_names)

        # 1. Non-negative scaling for Chi-Square test
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        # 2. Compute Mutual Information
        mi_scores = mutual_info_classif(X_scaled, y, random_state=self.random_state)

        # 3. Compute Chi-Square scores
        chi2_scores, _ = chi2(X_scaled, y)
        chi2_scores = np.nan_to_num(chi2_scores, nan=0.0)

        # 4. Train RF for SHAP / Tree-based importance
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=self.random_state, n_jobs=-1
        )
        rf.fit(X_scaled, y)

        # Compute TreeSHAP over sampled instances
        if len(X_scaled) > self.shap_sample_size:
            sample_idx = np.random.RandomState(self.random_state).choice(
                len(X_scaled), size=self.shap_sample_size, replace=False
            )
            X_sample = X_scaled[sample_idx]
        else:
            X_sample = X_scaled

        try:
            explainer = shap.TreeExplainer(rf)
            shap_values = explainer.shap_values(X_sample)
            # Handle multi-class / binary list outputs
            if isinstance(shap_values, list):
                shap_scores = np.mean(np.abs(shap_values[1]), axis=0)
            elif shap_values.ndim == 3:
                shap_scores = np.mean(np.abs(shap_values[:, :, 1]), axis=0)
            else:
                shap_scores = np.mean(np.abs(shap_values), axis=0)
        except Exception:
            # Fallback to RF Gini feature importances if TreeExplainer fails
            shap_scores = rf.feature_importances_

        # 5. Convert raw scores to normalized ranks [0, 1]
        def to_norm_rank(scores: np.ndarray) -> np.ndarray:
            ranks = pd.Series(scores).rank(ascending=True).values
            return ranks / max(float(n_features), 1.0)

        rank_mi = to_norm_rank(mi_scores)
        rank_chi2 = to_norm_rank(chi2_scores)
        rank_shap = to_norm_rank(shap_scores)

        # 6. Weighted Rank Aggregation
        composite_score = (
            self.w_mi * rank_mi + self.w_chi2 * rank_chi2 + self.w_shap * rank_shap
        )

        ranking_df = pd.DataFrame(
            {
                "feature": feature_names,
                "mi_score": mi_scores,
                "chi2_score": chi2_scores,
                "shap_score": shap_scores,
                "composite_score": composite_score,
            }
        ).sort_values(by="composite_score", ascending=False)

        self.feature_rankings_ = ranking_df
        self.selected_features_ = ranking_df.head(self.top_k)["feature"].tolist()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Filter input DataFrame to the selected Top-K features."""
        if not self.selected_features_:
            raise ValueError("HybridFeatureSelector has not been fitted yet.")
        return X[self.selected_features_]

    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

