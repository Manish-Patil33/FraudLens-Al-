"""
FraudLens AI - Synthetic Financial Transaction Dataset Generator
Produces a realistic financial transaction stream mirroring Kaggle PaySim
and real-world mobile money / banking transfer logs.
"""

import numpy as np
import pandas as pd
import os
import json

def generate_financial_data(
    n_samples: int = 60000,
    fraud_rate: float = 0.005,
    random_state: int = 42,
    output_path: str = "data/raw/financial_transactions.csv"
) -> pd.DataFrame:
    """
    Generates synthetic financial transaction logs with realistic fraud dynamics.
    
    Features:
    - step: Time simulation unit (1 step = 1 hour, spans 720 hours / 30 days)
    - type: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER
    - amount: Transaction amount (log-normal distribution)
    - nameOrig: Customer identifier (C + 10 digits)
    - oldbalanceOrg: Originator balance before transaction
    - newbalanceOrig: Originator balance after transaction
    - nameDest: Recipient identifier (C + 10 digits or M + 10 digits for merchants)
    - oldbalanceDest: Recipient balance before transaction
    - newbalanceDest: Recipient balance after transaction
    - device_trust_score: Trust level of client device [0.0, 1.0]
    - location_risk_score: Anomaly score for geo-location/IP mismatch [0.0, 1.0]
    - transaction_channel: MOBILE_APP, WEB_PORTAL, ATM, POS_TERMINAL
    - is_fraud: Binary target (1 = Fraudulent, 0 = Legitimate)
    - is_flagged_fraud: Legacy rule flag (amount > 200,000 in Transfer)
    """
    np.random.seed(random_state)
    n_fraud = int(n_samples * fraud_rate)
    n_legit = n_samples - n_fraud

    # 1. Legitimate Transactions
    legit_types = np.random.choice(
        ['PAYMENT', 'CASH_OUT', 'CASH_IN', 'TRANSFER', 'DEBIT'],
        size=n_legit,
        p=[0.40, 0.25, 0.20, 0.12, 0.03]
    )
    
    # Amounts follow lognormal distribution: median ~$75, tail up to 100,000
    legit_amounts = np.round(np.random.lognormal(mean=4.5, sigma=1.2, size=n_legit), 2)
    # Clip negative or 0
    legit_amounts = np.clip(legit_amounts, 1.0, 500000.0)
    
    # Originator balances
    legit_old_orig = np.round(np.random.exponential(scale=20000.0, size=n_legit) + legit_amounts * np.random.uniform(0.5, 3.0, size=n_legit), 2)
    
    # Compute new originator balance based on type
    legit_new_orig = np.zeros(n_legit)
    for i, t in enumerate(legit_types):
        if t in ['PAYMENT', 'CASH_OUT', 'TRANSFER', 'DEBIT']:
            legit_new_orig[i] = max(0.0, round(legit_old_orig[i] - legit_amounts[i], 2))
        else: # CASH_IN
            legit_new_orig[i] = round(legit_old_orig[i] + legit_amounts[i], 2)
            
    # Destination balances
    legit_old_dest = np.round(np.random.exponential(scale=35000.0, size=n_legit), 2)
    legit_new_dest = np.zeros(n_legit)
    for i, t in enumerate(legit_types):
        if t in ['PAYMENT', 'CASH_IN', 'TRANSFER', 'DEBIT']:
            legit_new_dest[i] = round(legit_old_dest[i] + legit_amounts[i], 2)
        else: # CASH_OUT
            legit_new_dest[i] = max(0.0, round(legit_old_dest[i] - legit_amounts[i], 2))
            
    # Normal device trust score (high, mean 0.85) and low location risk (mean 0.15)
    legit_dev_trust = np.clip(np.random.beta(a=8, b=2, size=n_legit), 0.05, 1.0)
    legit_loc_risk = np.clip(np.random.beta(a=2, b=9, size=n_legit), 0.0, 0.95)
    
    legit_channels = np.random.choice(
        ['MOBILE_APP', 'WEB_PORTAL', 'POS_TERMINAL', 'ATM'],
        size=n_legit,
        p=[0.55, 0.25, 0.15, 0.05]
    )
    legit_steps = np.random.randint(1, 721, size=n_legit) # 30 days of hourly steps

    # 2. Fraudulent Transactions
    # In financial crime, fraud predominantly hits TRANSFER and CASH_OUT (illicit siphon & liquidation)
    fraud_types = np.random.choice(['TRANSFER', 'CASH_OUT'], size=n_fraud, p=[0.55, 0.45])
    
    # Fraudulent amounts are significantly larger (drain account or large lump sums)
    fraud_amounts = np.round(np.random.lognormal(mean=9.5, sigma=1.3, size=n_fraud), 2)
    fraud_amounts = np.clip(fraud_amounts, 500.0, 1500000.0)
    
    # In fraud, attackers often drain account entirely (newbalanceOrig = 0)
    fraud_old_orig = fraud_amounts.copy()
    # 35% of fraud cases have slightly more balance, but 65% are exact liquidation
    drain_mask = np.random.rand(n_fraud) > 0.35
    fraud_old_orig[~drain_mask] = np.round(fraud_amounts[~drain_mask] + np.random.uniform(500, 10000, size=np.sum(~drain_mask)), 2)
    
    fraud_new_orig = np.zeros(n_fraud)
    for i in range(n_fraud):
        if drain_mask[i]:
            fraud_new_orig[i] = 0.0
        else:
            fraud_new_orig[i] = max(0.0, round(fraud_old_orig[i] - fraud_amounts[i], 2))
            
    # Destination in fraud: Mules often have 0 initial balance, and frequently cash out immediately leaving balance 0!
    dest_mule_zero = np.random.rand(n_fraud) > 0.40
    fraud_old_dest = np.zeros(n_fraud)
    fraud_old_dest[~dest_mule_zero] = np.round(np.random.exponential(scale=10000.0, size=np.sum(~dest_mule_zero)), 2)
    
    fraud_new_dest = np.zeros(n_fraud)
    for i in range(n_fraud):
        if np.random.rand() > 0.5: # mule account drained or kept off-ledger
            fraud_new_dest[i] = 0.0
        else:
            fraud_new_dest[i] = round(fraud_old_dest[i] + fraud_amounts[i], 2)
            
    # Fraud device trust is low, location risk is elevated
    fraud_dev_trust = np.clip(np.random.beta(a=2, b=7, size=n_fraud), 0.01, 0.85)
    fraud_loc_risk = np.clip(np.random.beta(a=7, b=2, size=n_fraud), 0.15, 0.99)
    
    fraud_channels = np.random.choice(
        ['MOBILE_APP', 'WEB_PORTAL', 'POS_TERMINAL', 'ATM'],
        size=n_fraud,
        p=[0.30, 0.60, 0.05, 0.05]
    )
    # Fraudsters frequently operate during off-peak night hours (step % 24 in [0, 5])
    night_steps = np.random.choice([h for h in range(1, 721) if (h % 24) in [0, 1, 2, 3, 4, 5]], size=int(n_fraud * 0.60))
    day_steps = np.random.choice([h for h in range(1, 721) if (h % 24) not in [0, 1, 2, 3, 4, 5]], size=n_fraud - len(night_steps))
    fraud_steps = np.concatenate([night_steps, day_steps])
    np.random.shuffle(fraud_steps)

    # Compile data
    df_legit = pd.DataFrame({
        'step': legit_steps,
        'type': legit_types,
        'amount': legit_amounts,
        'oldbalanceOrg': legit_old_orig,
        'newbalanceOrig': legit_new_orig,
        'oldbalanceDest': legit_old_dest,
        'newbalanceDest': legit_new_dest,
        'device_trust_score': legit_dev_trust,
        'location_risk_score': legit_loc_risk,
        'transaction_channel': legit_channels,
        'is_fraud': 0
    })
    
    df_fraud = pd.DataFrame({
        'step': fraud_steps,
        'type': fraud_types,
        'amount': fraud_amounts,
        'oldbalanceOrg': fraud_old_orig,
        'newbalanceOrig': fraud_new_orig,
        'oldbalanceDest': fraud_old_dest,
        'newbalanceDest': fraud_new_dest,
        'device_trust_score': fraud_dev_trust,
        'location_risk_score': fraud_loc_risk,
        'transaction_channel': fraud_channels,
        'is_fraud': 1
    })

    df = pd.concat([df_legit, df_fraud], ignore_index=True)
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    # Generate customer and merchant IDs
    df['nameOrig'] = ['C' + str(1000000000 + i) for i in range(len(df))]
    dest_prefix = np.where(df['type'] == 'PAYMENT', 'M', 'C')
    df['nameDest'] = [f"{dest_prefix[i]}{1000000000 + (i * 3) % 99999999}" for i in range(len(df))]
    
    # Rule flag: transactions > 200,000 in TRANSFER
    df['is_flagged_fraud'] = np.where((df['type'] == 'TRANSFER') & (df['amount'] > 200000), 1, 0)
    
    # Reorder columns to match standard schema
    cols = [
        'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
        'nameDest', 'oldbalanceDest', 'newbalanceDest', 'device_trust_score',
        'location_risk_score', 'transaction_channel', 'is_flagged_fraud', 'is_fraud'
    ]
    df = df[cols]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    # Save Data Dictionary
    dict_path = "data/processed/data_dictionary.json"
    os.makedirs(os.path.dirname(dict_path), exist_ok=True)
    data_dict = {
        "step": "Time step mapping 1 unit = 1 hour (total 720 hours = 30 days)",
        "type": "Transaction type: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER",
        "amount": "Transaction value in currency units",
        "nameOrig": "Customer initiator account ID (starts with C)",
        "oldbalanceOrg": "Account balance of origin before transaction",
        "newbalanceOrig": "Account balance of origin after transaction",
        "nameDest": "Recipient account ID (starts with C for customer, M for merchant)",
        "oldbalanceDest": "Account balance of recipient before transaction",
        "newbalanceDest": "Account balance of recipient after transaction",
        "device_trust_score": "Continuous score [0-1] based on device fingerprinting, TLS, and browser history",
        "location_risk_score": "Continuous score [0-1] based on IP geo-velocity and VPN/proxy detection",
        "transaction_channel": "Access channel: MOBILE_APP, WEB_PORTAL, POS_TERMINAL, ATM",
        "is_flagged_fraud": "Rule-based legacy flag: triggers when TRANSFER amount > 200,000",
        "is_fraud": "Target ground truth label: 1 if fraudulent transaction, 0 if legitimate"
    }
    with open(dict_path, "w") as f:
        json.dump(data_dict, f, indent=4)
        
    print(f"Dataset successfully created at {output_path} with {len(df)} records ({df['is_fraud'].sum()} fraud, {len(df) - df['is_fraud'].sum()} legit).")
    return df

if __name__ == "__main__":
    generate_financial_data()

