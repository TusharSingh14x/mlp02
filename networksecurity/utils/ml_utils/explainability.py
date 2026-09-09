from typing import Any

import numpy as np
import pandas as pd
import shap


def explain_prediction(model: Any, preprocessor: Any, features: pd.DataFrame, limit: int = 8) -> dict:
    """Return local SHAP contributions for the phishing class.

    Positive contributions increase the model's phishing output; negative
    contributions push the prediction toward legitimate.
    """
    transformed = preprocessor.transform(features)
    feature_names = list(features.columns)
    method = "model_feature_importance"
    base_value = None
    contributions = None

    try:
        if hasattr(model, "feature_importances_"):
            shap_values = shap.TreeExplainer(model)(transformed)
            class_index = list(model.classes_).index(0) if 0 in model.classes_ else 0
            contributions = shap_values.values[0, :, class_index]
            base_value = float(np.asarray(shap_values.base_values[0]).reshape(-1)[class_index])
            method = "shap_tree_explainer"
        elif hasattr(model, "coef_"):
            shap_values = shap.LinearExplainer(model, transformed)(transformed)
            class_index = list(model.classes_).index(0) if 0 in model.classes_ else 0
            values = shap_values.values
            contributions = values[0, :, class_index] if values.ndim == 3 else values[0]
            base_value = float(np.asarray(shap_values.base_values[0]).reshape(-1)[class_index])
            method = "shap_linear_explainer"
    except Exception:
        contributions = None

    if contributions is None:
        importances = getattr(model, "feature_importances_", None)
        if importances is None and hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        if importances is None:
            return {"method": "unavailable", "base_value": None, "features": []}
        contributions = np.asarray(importances, dtype=float)

    ranked = sorted(
        zip(feature_names, features.iloc[0].tolist(), np.asarray(contributions, dtype=float)),
        key=lambda item: abs(item[2]),
        reverse=True,
    )[:limit]
    return {
        "method": method,
        "base_value": base_value,
        "features": [
            {
                "feature": name,
                "value": value,
                "contribution": round(float(contribution), 6),
                "direction": "phishing" if contribution > 0 else "legitimate",
            }
            for name, value, contribution in ranked
        ],
    }