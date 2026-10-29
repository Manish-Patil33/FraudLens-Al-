"""
FraudLens AI - Preprocessing and Data Pipeline
Handles data cleaning, one-hot encoding, and robust scaling without data leakage.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from src.feature_engineering import engineer_features, get_feature_columns

class FraudDataPipeline:
    """
    Modular preprocessing pipeline for FraudLens AI.
    Fits scalers and encoders strictly on the training set.
    """
    def __init__(self, target_col: str = "is_fraud"):
        self.target_col = target_col
        self.scaler = RobustScaler()
        self.feature_columns = None
        self.expected_types = ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
        self.expected_channels = ['ATM', 'MOBILE_APP', 'POS_TERMINAL', 'WEB_PORTAL']

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans data: removes exact duplicates, imputes missing values if any.
        """
        df = df.copy()
        initial_len = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_len:
            print(f"Dropped {initial_len - len(df)} duplicate records.")
            
        # Numerical null imputation with median, categorical with mode
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def transform_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encodes transaction types and channels with fixed known schema.
        """
        df = df.copy()
        for t in self.expected_types:
            df[f'type_{t}'] = (df['type'] == t).astype(int)
        for c in self.expected_channels:
            df[f'channel_{c}'] = (df['transaction_channel'] == c).astype(int)
        return df

    def prepare_features(self, df: pd.DataFrame, is_train: bool = True):
        """
        Full feature transformation: cleaning, feature engineering, encoding, and scaling.
        """
        df_clean = self.clean_data(df)
        df_engineered = engineer_features(df_clean)
        df_encoded = self.transform_categorical(df_engineered)

        feature_cols = get_feature_columns()
        self.feature_columns = feature_cols
        
        # Verify all feature columns exist
        for col in feature_cols:
            if col not in df_encoded.columns:
                df_encoded[col] = 0.0

        X = df_encoded[feature_cols].copy()
        
        # Scale numerical features
        scale_cols = [
            'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
            'error_balance_orig', 'error_balance_dest', 'amount_to_orig_ratio',
            'log_amount', 'log_oldbalanceOrg', 'log_oldbalanceDest'
        ]
        
        if is_train:
            self.scaler.fit(X[scale_cols])
            
        X[scale_cols] = self.scaler.transform(X[scale_cols])
        
        y = None
        if self.target_col in df_encoded.columns:
            y = df_encoded[self.target_col].values

        return X, y

    def split_and_prepare(
        self,
        df: pd.DataFrame,
        test_size: float = 0.20,
        random_state: int = 42
    ):
        """
        Performs stratified train-test split, then applies feature engineering and fit-transforms scaler.
        Strictly prevents data leakage.
        """
        print(f"Total dataset: {len(df)} records. Fraud rate: {df[self.target_col].mean()*100:.2f}%")
        
        # Split first to prevent data leakage!
        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df[self.target_col]
        )
        
        print(f"Training split: {len(train_df)} rows ({train_df[self.target_col].sum()} fraud).")
        print(f"Testing split: {len(test_df)} rows ({test_df[self.target_col].sum()} fraud).")

        X_train, y_train = self.prepare_features(train_df, is_train=True)
        X_test, y_test = self.prepare_features(test_df, is_train=False)

        return X_train, X_test, y_train, y_test

    def save(self, filepath: str = "models/preprocessor.joblib"):
        """Saves fitted preprocessor state."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"Preprocessor saved to {filepath}")

    @staticmethod
    def load(filepath: str = "models/preprocessor.joblib") -> "FraudDataPipeline":
        """Loads fitted preprocessor state."""
        return joblib.load(filepath)

