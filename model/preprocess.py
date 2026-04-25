import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

def load_and_preprocess(filepath: str, protected_col: str = 'race', target_col: str = 'loan_approved'):
    df = pd.read_csv(filepath, low_memory=False)

    # Validate that required columns exist
    if protected_col not in df.columns:
        raise ValueError(f"Protected column '{protected_col}' not found. Available: {df.columns.tolist()}")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Available: {df.columns.tolist()}")

    # Drop rows with nulls in key columns
    df = df.dropna(subset=[protected_col, target_col])

    # Target: must be binary (0/1)
    df['approved'] = df[target_col].astype(int)

    # Sensitive attribute
    sensitive = df[protected_col].astype(str)

    # Feature columns: everything numeric except the target and protected col
    exclude = [protected_col, target_col, 'approved', 'applicant_id']
    feature_cols = [
        col for col in df.columns
        if col not in exclude and pd.api.types.is_numeric_dtype(df[col])
    ]

    if not feature_cols:
        raise ValueError("No numeric feature columns found after excluding protected and target columns.")

    X = df[feature_cols].fillna(0)
    y = df['approved']

    return X, y, sensitive, df