import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

# Explicit allowlist: only these numeric columns are ever used as model features,
# regardless of what else exists in the uploaded CSV. Extend this list deliberately
# if you add new legitimate features later — don't let it auto-detect "everything numeric",
# since raw HMDA exports include tract-level demographic proxies (e.g.
# tract_minority_population_percent) that would leak race-correlated info into
# the model and undermine the fairness analysis.
ALLOWED_FEATURE_COLS = ["income", "loan_amount", "dti", "ltv"]
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

    # Feature columns: explicit allowlist, restricted to columns that actually exist
    feature_cols = [col for col in ALLOWED_FEATURE_COLS if col in df.columns]
    if not feature_cols:
        raise ValueError(
            f"None of the expected feature columns {ALLOWED_FEATURE_COLS} were found in the dataset. "
            f"Available columns: {df.columns.tolist()}"
        )

    X = df[feature_cols].fillna(0)
    y = df['approved']

    return X, y, sensitive, df