import numpy as np
import scipy.stats as stats
from typing import Dict, Any, List


def mcnemar_test(y_true: np.ndarray, y_pred_model_a: np.ndarray, y_pred_model_b: np.ndarray) -> Dict[str, Any]:
    """
    Computes McNemar's test for paired binary classification outcomes.
    Evaluates whether Model A and Model B have statistically significant differences
    in their discordance matrix (cells b and c).
    """
    correct_a = (y_pred_model_a == y_true)
    correct_b = (y_pred_model_b == y_true)

    # Contingency Table:
    # a: both correct, b: A correct & B incorrect
    # c: A incorrect & B correct, d: both incorrect
    a = int(np.sum(correct_a & correct_b))
    b = int(np.sum(correct_a & (~correct_b)))
    c = int(np.sum((~correct_a) & correct_b))
    d = int(np.sum((~correct_a) & (~correct_b)))

    # Edwards continuity correction
    if (b + c) == 0:
        chi2_stat = 0.0
        p_val = 1.0
    else:
        chi2_stat = ((abs(b - c) - 1.0) ** 2) / float(b + c)
        p_val = stats.chi2.sf(chi2_stat, df=1)

    return {
        "contingency_table": [[a, b], [c, d]],
        "discordant_b (A correct, B wrong)": b,
        "discordant_c (A wrong, B correct)": c,
        "chi2_statistic": round(float(chi2_stat), 4),
        "p_value": float(p_val),
        "statistically_significant": bool(p_val < 0.05)
    }


def paired_t_test_cross_val(scores_model_a: List[float], scores_model_b: List[float]) -> Dict[str, Any]:
    """
    Computes a two-tailed paired t-test across K-fold cross-validation runs.
    """
    diffs = np.array(scores_model_a) - np.array(scores_model_b)
    t_stat, p_val = stats.ttest_rel(scores_model_a, scores_model_b)
    return {
        "mean_difference": round(float(np.mean(diffs)), 6),
        "std_difference": round(float(np.std(diffs, ddof=1)), 6),
        "t_statistic": round(float(t_stat), 4),
        "p_value": float(p_val),
        "statistically_significant": bool(p_val < 0.05)
    }

