import pandas as pd

def run_counterfactual(model, scaler, feature_cols: list, applicant_dict: dict,
                        attribute_col: str, original_val: str, flipped_val: str):
    """
    Takes a single applicant's data, predicts their outcome, then flips
    a specified attribute and predicts again to test for individual fairness.

    Important limitation: this model is trained only on `feature_cols`
    (income, loan_amount, dti, ltv) — race/gender are NOT model inputs,
    only used for measuring group-level fairness metrics elsewhere. If
    attribute_col isn't one of feature_cols, flipping it cannot change the
    model's prediction, because the model never sees that value. Returning
    "bias_detected: False" in that case would be misleading — it wouldn't
    mean the model is fair, it would mean this test isn't capable of
    measuring that attribute's effect at all. So we surface that explicitly
    instead of silently returning a false negative.
    """
    if attribute_col not in feature_cols:
        return {
            "tested": False,
            "reason": (
                f"'{attribute_col}' is not a feature this model uses for prediction "
                f"(model inputs are: {feature_cols}). Flipping it cannot change the "
                f"model's decision by construction, so this test cannot detect direct "
                f"discrimination on this attribute. It also cannot rule out indirect/proxy "
                f"discrimination — where '{attribute_col}' correlates with one of the "
                f"model's actual inputs — since that requires a different kind of analysis."
            ),
            "original_decision": None,
            "flipped_decision": None,
            "changed": None,
            "bias_detected": None,
        }

    applicant_df = pd.DataFrame([applicant_dict])[feature_cols]

    original = applicant_df.copy()
    flipped = applicant_df.copy()
    flipped[attribute_col] = flipped_val
    # keep types consistent with original_val if the caller passed it for reference
    _ = original_val

    # Apply the SAME fitted scaler used at training time — the model was
    # trained on scaled features, so raw applicant values would otherwise
    # produce meaningless predictions.
    original_scaled = pd.DataFrame(scaler.transform(original), columns=feature_cols)
    flipped_scaled = pd.DataFrame(scaler.transform(flipped), columns=feature_cols)

    pred_original = model.predict(original_scaled)[0]
    pred_flipped = model.predict(flipped_scaled)[0]

    decision_changed = bool(pred_original != pred_flipped)

    return {
        "tested": True,
        "reason": None,
        "original_decision": "approved" if pred_original == 1 else "denied",
        "flipped_decision": "approved" if pred_flipped == 1 else "denied",
        "changed": decision_changed,
        "bias_detected": decision_changed,
    }