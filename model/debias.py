from fairlearn.reductions import ExponentiatedGradient, DemographicParity
from sklearn.linear_model import LogisticRegression
from model.metrics import compute_fairness_metrics

# Floor so the bound never hits exactly 0, which can make the
# ExponentiatedGradient problem infeasible or force excessive accuracy loss
# chasing an unreachable target.
MIN_BOUND = 0.005

def run_debiasing(X_train, y_train, s_train, X_test, y_test, s_test,
                   fairness_weight: float, baseline_dp_gap: float):
    """
    Runs in-processing debiasing based on the fairness_weight slider value.

    The difference_bound is scaled relative to the baseline model's own
    demographic parity gap, rather than a fixed constant. This keeps the
    slider meaningful regardless of dataset: at fairness_weight=0, the bound
    equals the baseline gap (no constraint beyond what already exists, so
    the model is effectively unchanged); at fairness_weight=1, the bound
    shrinks toward MIN_BOUND (near-strict fairness).
    """
    bound = max(MIN_BOUND, baseline_dp_gap * (1 - fairness_weight))
    constraint = DemographicParity(difference_bound=bound)

    mitigator = ExponentiatedGradient(
        LogisticRegression(max_iter=1000),
        constraints=constraint
    )
    mitigator.fit(X_train, y_train, sensitive_features=s_train)

    y_pred_fair = mitigator.predict(X_test)
    metrics = compute_fairness_metrics(y_test, y_pred_fair, s_test)
    metrics["difference_bound_used"] = float(bound)  # useful for debugging/UI display

    return mitigator, metrics