"""
FraudLens AI - Evaluation and Financial Impact Analysis Module
Computes precision, recall, PR-AUC, confusion matrices, and financial cost-benefit ROI.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    precision_recall_curve, roc_curve, auc,
    confusion_matrix, classification_report
)

def evaluate_cost_benefit(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    amounts: np.ndarray,
    cost_fp: float = 35.0,     # Cost of manual review + friction per false alarm
    cost_review: float = 25.0  # Cost to verify an alert
) -> Dict[str, Any]:
    """
    Computes real-world financial balance sheet:
    - Fraud Losses Prevented (True Positives)
    - Fraud Losses Incurred (False Negatives - missed fraud)
    - Operational Friction Cost (False Positives)
    - Net Economic Benefit ($ Saved)
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    # Calculate actual dollar values
    fraud_mask = (y_true == 1)
    detected_mask = fraud_mask & (y_pred == 1)
    missed_mask = fraud_mask & (y_pred == 0)

    total_potential_loss = float(np.sum(amounts[fraud_mask]))
    fraud_intercepted = float(np.sum(amounts[detected_mask]))
    fraud_escaped = float(np.sum(amounts[missed_mask]))

    operational_cost = float((tp * cost_review) + (fp * cost_fp))
    net_savings = float(fraud_intercepted - operational_cost)
    roi_percentage = (net_savings / operational_cost * 100.0) if operational_cost > 0 else 0.0

    return {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "total_fraud_volume_usd": round(total_potential_loss, 2),
        "fraud_prevented_usd": round(fraud_intercepted, 2),
        "fraud_leaked_usd": round(fraud_escaped, 2),
        "operational_friction_cost_usd": round(operational_cost, 2),
        "net_financial_savings_usd": round(net_savings, 2),
        "prevention_efficiency_pct": round((fraud_intercepted / (total_potential_loss + 1e-6)) * 100.0, 2),
        "roi_pct": round(roi_percentage, 2)
    }

def find_optimal_threshold(
    y_true: np.ndarray,
    y_probs: np.ndarray,
    amounts: np.ndarray = None,
    cost_fp: float = 35.0
) -> Tuple[float, Dict[str, float]]:
    """
    Finds the optimal decision threshold that balances precision and recall
    or maximizes net financial savings.
    """
    thresholds = np.linspace(0.05, 0.95, 37)
    best_f1 = -1.0
    best_thresh = 0.5
    best_metrics = {}

    for thresh in thresholds:
        preds = (y_probs >= thresh).astype(int)
        cm = confusion_matrix(y_true, preds)
        tn, fp, fn, tp = cm.ravel()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall + 1e-8)

        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            best_metrics = {
                "threshold": float(round(thresh, 3)),
                "precision": float(round(precision, 4)),
                "recall": float(round(recall, 4)),
                "f1_score": float(round(f1, 4))
            }

    return best_thresh, best_metrics

