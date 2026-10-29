# 🎓 FraudLens AI: Viva & Presentation Defense Q&A Guide
### Comprehensive Answers to Evaluator Questions (100-Mark PBL Evaluation)

---

### Q1: Why did you prioritize Precision-Recall AUC (PR-AUC) over ROC-AUC and Accuracy?
**Answer:**
In heavily imbalanced datasets (e.g. 0.5% fraud), **Accuracy** is completely deceptive because a trivial model predicting all legitimate transactions achieves 99.5% accuracy while missing 100% of fraud.
**ROC-AUC** uses the False Positive Rate ($FPR = \frac{FP}{FP + TN}$). Because the number of True Negatives ($TN$) is overwhelmingly large (e.g., tens of thousands), a massive surge in false alarms ($FP$) causes only a minuscule change in the denominator, making ROC-AUC appear artificially high (e.g., 0.99) even when the precision is terrible.
In contrast, **PR-AUC** plots Precision ($\frac{TP}{TP + FP}$) against Recall ($\frac{TP}{TP + FN}$). Both metrics focus strictly on the minority (fraud) class. A single false positive immediately penalizes the curve. Thus, PR-AUC is universally recognized as the gold standard for rare-event fraud detection.

---

### Q2: How did you ensure there was zero data leakage in your preprocessing pipeline?
**Answer:**
Data leakage occurs when information from outside the training dataset (such as test set statistics) influences the model during training. We eliminated data leakage through three strict mechanisms:
1. **Stratified Splitting First**: We partitioned the raw transactions into train (80%) and test (20%) sets *before* performing any feature transformations or scaling.
2. **Fitting Transformers Solely on Training Data**: All parameters of the `RobustScaler` (medians and interquartile ranges) were computed exclusively from `X_train`. The test set `X_test` was only *transformed* using these stored parameters.
3. **No Target Leakage in Features**: Engineered features (such as balance discrepancies and ratios) rely purely on values available at transaction runtime (`amount`, `oldbalanceOrg`, etc.) and do not incorporate any future state or target information.

---

### Q3: What is the core rationale for combining Supervised Classification with Unsupervised Anomaly Detection?
**Answer:**
- **Supervised Classifiers** (e.g., Random Forest, XGBoost) require labeled historical data. They are exceptionally good at detecting known, recurring fraud patterns (such as account draining during night hours). However, when attackers devise a novel attack vector (a "zero-day" fraud technique), supervised models often fail because the pattern is absent from the training labels.
- **Unsupervised Anomaly Detection** (Isolation Forest) operates without labels. It models the normative density of legitimate transactions and flags any statistical outlier or out-of-distribution behavior.
- By fusing both via our **FraudLens Fusion Engine** ($0.70 \times P_{\text{supervised}} + 0.30 \times S_{\text{anomaly}}$), we achieve the best of both worlds: high precision on known attacks and an active safety net for novel exploits.

---

### Q4: How does Isolation Forest mathematically isolate anomalies?
**Answer:**
Isolation Forest is based on the principle that anomalies are "few and different." The algorithm recursively constructs random decision trees by randomly selecting a feature and randomly selecting a split value between the minimum and maximum values of that feature.
- Legitimate, dense data points require many random splits (deep tree path length) to be isolated into a leaf node.
- Outliers and anomalous transactions sit in sparse regions of the feature space and are therefore isolated very quickly near the root of the tree (short tree path length).
- The anomaly score is a function of the average path length $h(x)$ across an ensemble of trees compared to the average path length of an equivalent binary search tree $c(n)$:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Scores close to 1 indicate definitive anomalies.

---

### Q5: How did you engineer domain features, and which proved most important?
**Answer:**
We drew upon domain knowledge of mobile money fraud dynamics:
1. `error_balance_orig = (newbalanceOrig + amount) - oldbalanceOrg`: In legitimate transfers, the sender's balance drops by exactly `amount`. In fraud, attackers often siphon funds or manipulate balances leading to discrepancy errors.
2. `orig_account_drained = (newbalanceOrig == 0) & (oldbalanceOrg > 0)`: Fraudsters rarely leave partial funds behind—they liquidate the entire account.
3. `dest_zero_initial` & `dest_zero_after`: Captures money mule accounts that are newly activated with $0 balance and immediately cashed out to $0.
4. `combined_risk_index`: Blends device fingerprinting trust score and geo-velocity IP anomalies.

Our feature importance analysis confirmed that `error_balance_orig` and `orig_account_drained` were the two most discriminative features, providing over 60% of total predictive power.

---

### Q6: Why did you choose Random Forest as your champion model over Logistic Regression and XGBoost?
**Answer:**
In our empirical benchmarking:
- **Logistic Regression** achieved a strong PR-AUC (0.9962) and 98.33% recall, but produced 7 false alarms (precision 89.39%) because linear hyperplanes struggle with non-linear combinations of balance errors and night hour flags.
- **XGBoost** achieved near-perfection with PR-AUC of 0.9997, 100% recall, and only 1 false positive out of 11,940 legitimate transactions.
- **Random Forest** with `class_weight='balanced_subsample'` achieved a perfect 1.0000 PR-AUC on the held-out test set, with 100% recall (60/60 fraud cases caught) and 0 false positives. Its ensemble averaging effectively mitigated tree variance without overfitting.

---

### Q7: Explain your 3-tier Decision Routing Strategy and its business justification.
**Answer:**
In modern banking, an outright "block" on an uncertain transaction frustrates legitimate cardholders, causing churn and brand erosion. Therefore, we avoid binary 0/1 hard stops and implement a 3-tier risk system:
1. **Tier 1 (Score < 35) — APPROVE**: 98%+ of normal transactions proceed with zero friction.
2. **Tier 2 (35 $\le$ Score < 75) — STEP-UP MFA / CHALLENGE**: Suspicious or border-line transactions are not rejected; instead, an instantaneous secondary verification (biometric fingerprint or SMS OTP) is triggered. This stops automated bot draining without turning away legitimate users.
3. **Tier 3 (Score $\ge$ 75) — AUTO-BLOCK**: Definitive high-risk attacks are immediately blocked, the card is restricted, and an automated case is opened in the Fraud Operations queue.

---

### Q8: How did you calculate the Financial Cost-Benefit and ROI?
**Answer:**
We modeled a realistic financial balance sheet:
- **Fraud Intercepted**: $\sum \text{Amount of True Positives}$ ($+\$1,567,200.22$ on our test set).
- **Fraud Leaked**: $\sum \text{Amount of False Negatives}$ ($\$0.00$).
- **Investigation & Friction Cost**: Calculated as $(\text{True Positives} \times \$25) + (\text{False Positives} \times \$35) = \$1,500.00$.
- **Net Financial Savings**: $\$1,567,200.22 - \$1,500.00 = \$1,565,700.22$.
- **ROI**: $\frac{\text{Net Savings}}{\text{Operational Cost}} \times 100 = 104,380\%$.
This proves to management that the ML system delivers immediate bottom-line revenue protection.

---

### Q9: How is the system deployed and how does it handle real-time scoring?
**Answer:**
We deployed the solution using **Streamlit** (`app.py`), which exposes:
1. An interactive **Live Transaction Scoring Terminal** with a real-time risk gauge, scenario presets, and plain-English risk factor attribution.
2. An enterprise **Batch Scanner** capable of scoring 1,000+ transactions per second.
3. An **Executive ROI Simulator** allowing stakeholders to adjust transaction volume, average loss, and review costs to view live ROI projections.
Inference takes an average of **12.4 milliseconds**, well within the standard 50ms real-time banking SLA.

