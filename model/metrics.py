import numpy as np
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
from sklearn.metrics import accuracy_score

def compute_fairness_metrics(y_true, y_pred, sensitive_features):
    """
    Computes accuracy, demographic parity gap, equalized odds gap, 
    and specific approval rates for each protected group.
    """
    dp_gap = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
    eo_gap = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive_features)
    accuracy = accuracy_score(y_true, y_pred)

    # Calculate specific approval rates by group (e.g., White: 0.74, Black: 0.51)
    approval_rates = {}
    unique_groups = sensitive_features.unique()
    
    for group in unique_groups:
        mask = (sensitive_features == group)
        # The mean of a binary prediction array (1s and 0s) gives the exact approval percentage
        rate = np.mean(y_pred[mask])
        approval_rates[group] = float(rate)

    return {
        "accuracy": float(accuracy),
        "demographic_parity_gap": float(dp_gap),
        "equalized_odds_gap": float(eo_gap),
        "approval_rates": approval_rates
    }