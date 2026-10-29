"""
FraudLens AI - Feature Engineering Module
Transforms raw transaction logs into rich behavioral and domain-specific features.
"""

import numpy as np
import pandas as pd

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies domain-engineered features without causing data leakage.
    Operates row-wise or on historical context.
    """
    df = df.copy()

    # 1. Financial Balance Discrepancy (Key PaySim / Banking Fraud Indicator)
    # Legitimate transfer should satisfy: newbalanceOrig = oldbalanceOrg - amount
    # If not, error_orig_balance != 0. Attackers often drain account or balance doesn't reconcile.
    df['error_balance_orig'] = (df['newbalanceOrig'] + df['amount']) - df['oldbalanceOrg']
    df['error_balance_dest'] = (df['oldbalanceDest'] + df['amount']) - df['newbalanceDest']

    # 2. Complete Liquidation & Mule Flags
    df['orig_account_drained'] = ((df['newbalanceOrig'] == 0) & (df['oldbalanceOrg'] > 0)).astype(int)
    df['dest_zero_initial'] = (df['oldbalanceDest'] == 0).astype(int)
    df['dest_zero_after'] = (df['newbalanceDest'] == 0).astype(int)

    # 3. Financial Ratio Features
    df['amount_to_orig_ratio'] = np.clip(df['amount'] / (df['oldbalanceOrg'] + 1.0), 0, 100.0)
    df['log_amount'] = np.log1p(df['amount'])
    df['log_oldbalanceOrg'] = np.log1p(df['oldbalanceOrg'])
    df['log_oldbalanceDest'] = np.log1p(df['oldbalanceDest'])

    # 4. Temporal Features
    df['hour_of_day'] = df['step'] % 24
    df['day_of_week'] = (df['step'] // 24) % 7
    df['is_night_hours'] = df['hour_of_day'].isin([0, 1, 2, 3, 4, 5]).astype(int)
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # 5. Cyber & Behavioral Risk Features
    df['combined_risk_index'] = ((1.0 - df['device_trust_score']) * 0.5 + df['location_risk_score'] * 0.5)
    df['untrusted_device_flag'] = (df['device_trust_score'] < 0.3).astype(int)
    df['high_location_risk_flag'] = (df['location_risk_score'] > 0.7).astype(int)

    # 6. High Value Transfer / Cash Out Indicator
    df['is_high_value_drain'] = (
        df['type'].isin(['TRANSFER', 'CASH_OUT']) & 
        (df['amount'] > 100000) & 
        (df['orig_account_drained'] == 1)
    ).astype(int)

    return df

def get_feature_columns():
    """
    Returns the list of final numerical and encoded feature names used in model training.
    """
    return [
        'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
        'device_trust_score', 'location_risk_score', 'is_flagged_fraud',
        'error_balance_orig', 'error_balance_dest', 'orig_account_drained',
        'dest_zero_initial', 'dest_zero_after', 'amount_to_orig_ratio',
        'log_amount', 'log_oldbalanceOrg', 'log_oldbalanceDest',
        'hour_of_day', 'day_of_week', 'is_night_hours', 'is_weekend',
        'combined_risk_index', 'untrusted_device_flag', 'high_location_risk_flag',
        'is_high_value_drain',
        'type_CASH_IN', 'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT', 'type_TRANSFER',
        'channel_ATM', 'channel_MOBILE_APP', 'channel_POS_TERMINAL', 'channel_WEB_PORTAL'
    ]

