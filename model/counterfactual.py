import pandas as pd

def run_counterfactual(model, applicant_dict: dict, attribute_col: str, original_val: str, flipped_val: str):
    """
    Takes a single applicant's data, predicts their outcome, then flips
    a specified attribute and predicts again to test for individual fairness.
    """
    # Convert the single applicant dictionary into a 1-row DataFrame
    applicant_df = pd.DataFrame([applicant_dict])
    
    # Create copies for the original and flipped states
    original = applicant_df.copy()
    flipped = applicant_df.copy()
    
    # Flip the targeted attribute (e.g., changing 'derived_race' from 'Black' to 'White')
    flipped[attribute_col] = flipped_val
    
    # Run predictions. We extract the first element [0] because predict returns an array
    pred_original = model.predict(original)[0]
    pred_flipped = model.predict(flipped)[0]
    
    # Check if the decision changed based *only* on the flipped attribute
    decision_changed = (pred_original != pred_flipped)
    
    return {
        "original_decision": "approved" if pred_original == 1 else "denied",
        "flipped_decision": "approved" if pred_flipped == 1 else "denied",
        "changed": bool(decision_changed),
        "bias_detected": bool(decision_changed)
    }