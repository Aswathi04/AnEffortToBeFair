import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder

def load_and_preprocess(filepath: str):
    """
    Loads HMDA CSV, filters, cleans, and encodes features for model training.
    """
    # Load CSV (low_memory=False prevents mixed type inference warnings on large files)
    df = pd.read_csv(filepath, low_memory=False)

    # Filter to only rows where action_taken IN (1,3)
    df = df[df['action_taken'].isin([1, 3])].copy()

    # Select only the required columns
    cols_to_keep = [
        'action_taken', 'derived_race', 'derived_sex',
        'loan_amount', 'income', 'loan_to_value_ratio',
        'debt_to_income_ratio', 'property_value', 'census_tract'
    ]
    df = df[cols_to_keep]

    # Handle nulls and 'Exempt' values for numeric columns
    for col in ['income', 'loan_to_value_ratio', 'property_value']:
        df = df.dropna(subset=[col])
        df = df[df[col] != 'Exempt']
        # Safely convert to float
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop any remaining rows that turned into NaN during numeric coercion
    df = df.dropna()

    # Preprocessing target: binary label. approved = 1 if action_taken == 1, else 0
    df['approved'] = (df['action_taken'] == 1).astype(int)

    # Encode DTI ratio ordinally (since it comes as string ranges like '20%-<30%')
    encoder = OrdinalEncoder()
    df[['debt_to_income_ratio']] = encoder.fit_transform(df[['debt_to_income_ratio']])

    # Sample size: use 50,000 rows max for prototype
    if len(df) > 50000:
        df = df.sample(n=50000, random_state=42)

    # Define Feature matrix (X), Target (y), and Sensitive Attributes (sensitive)
    # Exclude protected attributes and proxy variables from the training features
    feature_cols = [
        'loan_amount', 'income', 'loan_to_value_ratio', 
        'debt_to_income_ratio', 'property_value'
    ]
    
    X = df[feature_cols]
    y = df['approved']
    sensitive = df['derived_race']
    
    # Returning the raw dataframe as well so we have access to 'census_tract' and 
    # original text values for the counterfactual/proxy analysis endpoints later.
    return X, y, sensitive, df