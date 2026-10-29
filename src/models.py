"""
FraudLens AI - Model Architectures & Dual-Engine Fusion
Implements Supervised Classification, Unsupervised Anomaly Detection,
and the Unified FraudLens Hybrid Decision Engine.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, classification_report
)

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False


class FraudLensModelSuite:
    """
    Manages training, tuning, and serialization for:
    - Multiple Supervised Classifiers
    - Unsupervised Anomaly Detectors (Isolation Forest)
    - Hybrid Risk Scoring
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.supervised_models: Dict[str, Any] = {}
        self.anomaly_model: Any = None
        self.best_model_name: str = ""
        self.best_classifier: Any = None
        self.model_metrics: Dict[str, Dict[str, float]] = {}

    def initialize_models(self, scale_pos_weight: float = 100.0):
        """Initializes diverse model family with cost-sensitive weights."""
        models = {
            "Logistic_Regression": LogisticRegression(
                class_weight='balanced',
                max_iter=1000,
                random_state=self.random_state,
                C=0.1
            ),
            "Random_Forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                class_weight='balanced_subsample',
                random_state=self.random_state,
                n_jobs=-1
            ),
            "Gradient_Boosting": HistGradientBoostingClassifier(
                class_weight='balanced',
                max_iter=120,
                max_depth=8,
                random_state=self.random_state
            )
        }
        
        if XGB_AVAILABLE:
            models["XGBoost"] = XGBClassifier(
                n_estimators=120,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=scale_pos_weight,
                random_state=self.random_state,
                eval_metric="aucpr",
                n_jobs=-1
            )
            
        self.supervised_models = models
        
        # Unsupervised Anomaly Detector
        self.anomaly_model = IsolationForest(
            n_estimators=120,
            contamination=0.01,
            max_samples='auto',
            random_state=self.random_state,
            n_jobs=-1
        )

    def train_supervised(self, X_train: pd.DataFrame, y_train: np.ndarray, X_test: pd.DataFrame, y_test: np.ndarray):
        """
        Trains and evaluates all candidate supervised classifiers.
        Selects the best model based on Precision-Recall AUC (PR-AUC), which is the gold standard for rare fraud.
        """
        print("--- Training Supervised Classification Models ---")
        best_pr_auc = -1.0

        for name, model in self.supervised_models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            
            # Predict probabilities and classes
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            else:
                y_prob = model.decision_function(X_test)
                
            y_pred = (y_prob >= 0.5).astype(int)

            # Compute specialized evaluation metrics
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_prob)
            pr_auc = average_precision_score(y_test, y_prob)
            cm = confusion_matrix(y_test, y_pred)
            
            tn, fp, fn, tp = cm.ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            self.model_metrics[name] = {
                "precision": float(round(precision, 4)),
                "recall": float(round(recall, 4)),
                "f1": float(round(f1, 4)),
                "roc_auc": float(round(roc_auc, 4)),
                "pr_auc": float(round(pr_auc, 4)),
                "fpr": float(round(fpr, 5)),
                "tp": int(tp),
                "fp": int(fp),
                "tn": int(tn),
                "fn": int(fn)
            }
            print(f"[{name}] PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f} | Recall: {recall:.4f} | Precision: {precision:.4f} | FPR: {fpr:.5f}")

            if pr_auc > best_pr_auc:
                best_pr_auc = pr_auc
                self.best_model_name = name
                self.best_classifier = model

        print(f"\nChampion Supervised Model: {self.best_model_name} with PR-AUC: {best_pr_auc:.4f}")

    def train_unsupervised(self, X_train: pd.DataFrame, y_train: np.ndarray, X_test: pd.DataFrame, y_test: np.ndarray):
        """
        Trains Isolation Forest purely on legitimate or mixed transactions to detect zero-day anomalies.
        Isolation Forest assigns an anomaly score: lower values indicate abnormal behavior.
        """
        print("\n--- Training Unsupervised Anomaly Detection (Isolation Forest) ---")
        # Train on predominantly non-fraud or full training set
        self.anomaly_model.fit(X_train)
        
        # Decision function: lower values = more anomalous. Negative means outlier.
        anomaly_scores = self.anomaly_model.decision_function(X_test)
        
        # Invert and normalize to [0, 1] so 1 is highly anomalous
        # decision_function typically ranges from -0.5 to 0.5
        normalized_anomaly = 1.0 - (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min() + 1e-8)
        
        # Binary prediction (-1 outlier, 1 inlier)
        raw_pred = self.anomaly_model.predict(X_test)
        iso_pred = (raw_pred == -1).astype(int)
        
        pr_auc = average_precision_score(y_test, normalized_anomaly)
        roc_auc = roc_auc_score(y_test, normalized_anomaly)
        recall = recall_score(y_test, iso_pred)
        precision = precision_score(y_test, iso_pred, zero_division=0)
        
        self.model_metrics["Isolation_Forest"] = {
            "precision": float(round(precision, 4)),
            "recall": float(round(recall, 4)),
            "f1": float(round(f1_score(y_test, iso_pred), 4)),
            "roc_auc": float(round(roc_auc, 4)),
            "pr_auc": float(round(pr_auc, 4)),
            "fpr": float(round(np.mean(iso_pred[y_test == 0]), 5))
        }
        print(f"[Isolation Forest] Anomaly PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f} | Recall: {recall:.4f}")

    def predict_hybrid_risk(
        self,
        X: pd.DataFrame,
        weight_clf: float = 0.70,
        weight_ano: float = 0.30
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Unified FraudLens Decision Engine:
        Fuses Supervised Probabilities (known patterns) + Unsupervised Anomaly Score (novel exploits)
        into a composite Risk Score (0 to 100) and 3-Tier Policy Action:
        - Tier 1 (Score < 35): APPROVE (Low Friction)
        - Tier 2 (35 <= Score < 75): CHALLENGE MFA / REVIEW (Medium Risk)
        - Tier 3 (Score >= 75): AUTO-BLOCK (High Risk)
        """
        # Supervised probability
        if hasattr(self.best_classifier, "predict_proba"):
            p_clf = self.best_classifier.predict_proba(X)[:, 1]
        else:
            decision = self.best_classifier.decision_function(X)
            p_clf = 1.0 / (1.0 + np.exp(-decision))
            
        # Anomaly score normalized to [0, 1]
        dec_ano = self.anomaly_model.decision_function(X)
        p_ano = 1.0 - (dec_ano - dec_ano.min()) / (dec_ano.max() - dec_ano.min() + 1e-8)
        
        # Composite score 0 - 100
        composite_score = np.clip((weight_clf * p_clf + weight_ano * p_ano) * 100.0, 0.0, 100.0)
        
        # Action decisions
        actions = []
        for score in composite_score:
            if score < 35.0:
                actions.append("APPROVE")
            elif score < 75.0:
                actions.append("CHALLENGE_MFA")
            else:
                actions.append("AUTO_BLOCK")
                
        return composite_score, p_clf, np.array(actions)

    def save(self, model_dir: str = "models"):
        """Saves champion classifier, isolation forest, and metrics."""
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(self.best_classifier, os.path.join(model_dir, "best_classifier.joblib"))
        joblib.dump(self.anomaly_model, os.path.join(model_dir, "isolation_forest.joblib"))
        
        # Save metadata and metrics
        metadata = {
            "best_model_name": self.best_model_name,
            "metrics": self.model_metrics,
            "random_state": self.random_state
        }
        joblib.dump(metadata, os.path.join(model_dir, "model_metadata.joblib"))
        
        import json
        with open(os.path.join(model_dir, "model_metrics.json"), "w") as f:
            json.dump(self.model_metrics, f, indent=4)
            
        print(f"Models and metrics successfully saved to {model_dir}/")

