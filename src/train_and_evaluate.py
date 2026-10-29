"""
FraudLens AI - End-to-End Training, Evaluation & Visualizations
Executes complete Machine Learning lifecycle:
1. Exploratory Data Analysis & plot generation
2. Stratified train-test split & data preprocessing
3. Model training (Supervised classifiers + Unsupervised anomaly detection)
4. Rigorous validation & financial cost-benefit analysis
5. Model artifact serialization
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Headless backend for automated generation
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    roc_curve, precision_recall_curve, auc,
    confusion_matrix, classification_report
)

from src.preprocessing import FraudDataPipeline
from src.models import FraudLensModelSuite
from src.evaluate import evaluate_cost_benefit, find_optimal_threshold

def generate_eda_plots(df: pd.DataFrame, output_dir: str = "reports/figures"):
    """Generates and saves publication-quality EDA charts."""
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

    print("Generating EDA visualizations...")

    # 1. Class Distribution Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    fraud_counts = df['is_fraud'].value_counts()
    bars = ax.bar(['Legitimate (0)', 'Fraudulent (1)'], fraud_counts.values, color=['#2b5c8f', '#d9534f'], width=0.5)
    ax.set_yscale('log')
    ax.set_title("Class Distribution (Log Scale)\nSevere Imbalance: 99.5% Legit vs 0.5% Fraud", fontsize=13, weight='bold')
    ax.set_ylabel("Transaction Count (Log10)")
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval * 1.15, f"{yval:,} ({yval/len(df)*100:.2f}%)", ha='center', va='bottom', fontweight='semibold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_class_distribution.png"), dpi=300)
    plt.close()

    # 2. Fraud Proportion by Transaction Type
    fig, ax = plt.subplots(figsize=(8, 5))
    type_fraud = df.groupby('type')['is_fraud'].agg(['count', 'sum']).reset_index()
    type_fraud['fraud_pct'] = (type_fraud['sum'] / type_fraud['count']) * 100.0
    sns.barplot(data=type_fraud, x='type', y='fraud_pct', ax=ax, palette="Reds_r")
    ax.set_title("Fraud Occurrence Rate (%) by Transaction Type", fontsize=13, weight='bold')
    ax.set_ylabel("Fraud Rate (%)")
    ax.set_xlabel("Transaction Type")
    for i, row in type_fraud.iterrows():
        ax.text(i, row['fraud_pct'] + 0.05, f"{row['fraud_pct']:.2f}%\n({row['sum']}/{row['count']})", ha='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_transaction_type_fraud.png"), dpi=300)
    plt.close()

    # 3. Transaction Amount Comparison (Log-Scale Distribution)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.kdeplot(data=df[df['is_fraud'] == 0]['amount'], label='Legitimate', log_scale=True, color='#2b5c8f', fill=True, alpha=0.3, ax=ax)
    sns.kdeplot(data=df[df['is_fraud'] == 1]['amount'], label='Fraudulent', log_scale=True, color='#d9534f', fill=True, alpha=0.5, ax=ax)
    ax.set_title("Transaction Amount Density (Log Scale)", fontsize=13, weight='bold')
    ax.set_xlabel("Transaction Amount ($)")
    ax.set_ylabel("Kernel Density Estimate")
    ax.legend(title="Transaction Class")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_amount_distribution.png"), dpi=300)
    plt.close()

    # 4. Hourly / Temporal Attack Pattern
    fig, ax = plt.subplots(figsize=(9, 4.5))
    df_temp = df.copy()
    df_temp['hour'] = df_temp['step'] % 24
    hourly_fraud = df_temp.groupby('hour')['is_fraud'].mean() * 100.0
    ax.plot(hourly_fraud.index, hourly_fraud.values, marker='o', color='#c9302c', linewidth=2.5, markersize=6)
    ax.axvspan(0, 5, color='gray', alpha=0.15, label='Off-Peak Window (00:00 - 05:00)')
    ax.set_title("Fraud Frequency Across 24-Hour Cycle (Off-Peak Anomaly)", fontsize=13, weight='bold')
    ax.set_xlabel("Hour of Day (0 - 23)")
    ax.set_ylabel("Fraud Probability (%)")
    ax.set_xticks(range(0, 24))
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_temporal_night_pattern.png"), dpi=300)
    plt.close()

    # 5. Risk Correlation Matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    corr_cols = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'device_trust_score', 'location_risk_score', 'is_fraud']
    corr_matrix = df[corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, ax=ax, linewidths=0.5)
    ax.set_title("Feature Correlation Heatmap with Fraud Target", fontsize=13, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_correlation_heatmap.png"), dpi=300)
    plt.close()

    print("EDA plots saved successfully.")


def generate_evaluation_plots(
    model_suite: FraudLensModelSuite,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    output_dir: str = "reports/figures"
):
    """Generates ROC, PR-Curve, Confusion Matrix, and Cost-Benefit Visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Multi-Model ROC Curves
    plt.figure(figsize=(8, 6))
    for name, model in model_suite.supervised_models.items():
        if hasattr(model, "predict_proba"):
            y_score = model.predict_proba(X_test)[:, 1]
        else:
            y_score = model.decision_function(X_test)
        fpr, tpr, _ = roc_curve(y_test, y_score)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f"{name.replace('_', ' ')} (AUC = {roc_auc:.4f})")
    
    # Isolation Forest
    iso_scores = model_suite.anomaly_model.decision_function(X_test)
    iso_norm = 1.0 - (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min() + 1e-8)
    fpr_iso, tpr_iso, _ = roc_curve(y_test, iso_norm)
    plt.plot(fpr_iso, tpr_iso, lw=2, linestyle='--', color='purple', label=f"Isolation Forest [Anomaly] (AUC = {auc(fpr_iso, tpr_iso):.4f})")

    plt.plot([0, 1], [0, 1], color='navy', lw=1.5, linestyle=':', label='Random Baseline (AUC = 0.50)')
    plt.xlim([-0.01, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (FPR)', fontsize=12)
    plt.ylabel('True Positive Rate / Recall (TPR)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Comparison', fontsize=14, weight='bold')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eval_roc_curves.png"), dpi=300)
    plt.close()

    # 2. Precision-Recall Curves (Vital for Imbalanced Fraud)
    plt.figure(figsize=(8, 6))
    for name, model in model_suite.supervised_models.items():
        if hasattr(model, "predict_proba"):
            y_score = model.predict_proba(X_test)[:, 1]
        else:
            y_score = model.decision_function(X_test)
        prec, rec, _ = precision_recall_curve(y_test, y_score)
        pr_auc = auc(rec, prec)
        plt.plot(rec, prec, lw=2, label=f"{name.replace('_', ' ')} (PR-AUC = {pr_auc:.4f})")
        
    prec_iso, rec_iso, _ = precision_recall_curve(y_test, iso_norm)
    plt.plot(rec_iso, prec_iso, lw=2, linestyle='--', color='purple', label=f"Isolation Forest (PR-AUC = {auc(rec_iso, prec_iso):.4f})")

    baseline = np.mean(y_test)
    plt.plot([0, 1], [baseline, baseline], linestyle=':', color='black', label=f'Imbalance Baseline ({baseline*100:.2f}%)')
    plt.xlabel('Recall (Fraud Detection Rate)', fontsize=12)
    plt.ylabel('Precision (True Positive Alert Rate)', fontsize=12)
    plt.title('Precision-Recall Curves (Gold Standard for Rare Events)', fontsize=14, weight='bold')
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eval_precision_recall_curves.png"), dpi=300)
    plt.close()

    # 3. Champion Model Confusion Matrix
    plt.figure(figsize=(6, 5))
    best_clf = model_suite.best_classifier
    if hasattr(best_clf, "predict_proba"):
        y_prob = best_clf.predict_proba(X_test)[:, 1]
    else:
        y_prob = best_clf.decision_function(X_test)
    y_pred = (y_prob >= 0.5).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    
    sns.heatmap(cm, annot=True, fmt="d", cmap='Blues', cbar=False,
                xticklabels=['Pred Legit', 'Pred Fraud'],
                yticklabels=['Actual Legit', 'Actual Fraud'])
    plt.title(f"Confusion Matrix: Champion Model ({model_suite.best_model_name})", fontsize=13, weight='bold')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eval_confusion_matrix.png"), dpi=300)
    plt.close()

    # 4. Feature Importance Plot (Top 15 engineered features)
    if hasattr(best_clf, "feature_importances_"):
        plt.figure(figsize=(9, 6))
        feat_imp = pd.Series(best_clf.feature_importances_, index=X_test.columns).sort_values(ascending=False).head(15)
        sns.barplot(x=feat_imp.values, y=feat_imp.index, palette="Blues_r")
        plt.title(f"Top 15 Most Discriminative Features ({model_suite.best_model_name})", fontsize=13, weight='bold')
        plt.xlabel("Gini / Gain Importance")
        plt.ylabel("Engineered Feature")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "eval_feature_importance.png"), dpi=300)
        plt.close()


def run_pipeline():
    """Executes full pipeline."""
    data_path = "data/raw/financial_transactions.csv"
    if not os.path.exists(data_path):
        from src.data_generator import generate_financial_data
        generate_financial_data(output_path=data_path)

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} transactions from {data_path}.")

    # Generate EDA Visualizations
    generate_eda_plots(df)

    # Initialize and run data pipeline
    pipeline = FraudDataPipeline(target_col="is_fraud")
    X_train, X_test, y_train, y_test = pipeline.split_and_prepare(df, test_size=0.20, random_state=42)
    pipeline.save("models/preprocessor.joblib")

    # Save processed splits for reproducibility
    train_features = X_train.copy()
    train_features['is_fraud'] = y_train
    train_features.to_csv("data/processed/train_features.csv", index=False)
    
    test_features = X_test.copy()
    test_features['is_fraud'] = y_test
    test_features.to_csv("data/processed/test_features.csv", index=False)
    print("Saved processed features to data/processed/")

    # Initialize & train models
    model_suite = FraudLensModelSuite(random_state=42)
    model_suite.initialize_models(scale_pos_weight=150.0)
    model_suite.train_supervised(X_train, y_train, X_test, y_test)
    model_suite.train_unsupervised(X_train, y_train, X_test, y_test)

    # Generate Evaluation plots
    generate_evaluation_plots(model_suite, X_test, y_test)

    # Cost-Benefit Financial Analysis on Test Set
    test_amounts = df.loc[X_test.index, 'amount'].values if hasattr(X_test, "index") else np.ones(len(y_test)) * 1000
    if hasattr(model_suite.best_classifier, "predict_proba"):
        y_prob = model_suite.best_classifier.predict_proba(X_test)[:, 1]
    else:
        y_prob = model_suite.best_classifier.decision_function(X_test)
        
    best_thresh, best_metrics = find_optimal_threshold(y_test, y_prob)
    financial_roi = evaluate_cost_benefit(y_test, (y_prob >= best_thresh).astype(int), test_amounts)

    print("\n================ FINANCIAL ROI BALANCE SHEET ================")
    print(f"Optimal Decision Threshold: {best_thresh:.3f}")
    print(f"Total Fraud Volume at Risk: ${financial_roi['total_fraud_volume_usd']:,.2f}")
    print(f"Fraud Loss Intercepted:     ${financial_roi['fraud_prevented_usd']:,.2f}")
    print(f"Fraud Leaked (FN Loss):     ${financial_roi['fraud_leaked_usd']:,.2f}")
    print(f"Operational Friction Cost:  ${financial_roi['operational_friction_cost_usd']:,.2f}")
    print(f"NET FINANCIAL SAVINGS:      ${financial_roi['net_financial_savings_usd']:,.2f}")
    print(f"Fraud Prevention Rate:      {financial_roi['prevention_efficiency_pct']:.2f}%")
    print(f"Return on Investment (ROI): {financial_roi['roi_pct']:,.1f}%")
    print("=============================================================")

    # Save models and financial evaluation
    model_suite.save("models")
    with open("models/financial_roi.json", "w") as f:
        json.dump(financial_roi, f, indent=4)

    print("\nEnd-to-End Pipeline successfully executed!")

if __name__ == "__main__":
    run_pipeline()
