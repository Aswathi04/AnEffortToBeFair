from fairlearn.reductions import ExponentiatedGradient, DemographicParity
from sklearn.linear_model import LogisticRegression
from model.metrics import compute_fairness_metrics

def run_debiasing(X_train, y_train, s_train, X_test, y_test, s_test, fairness_weight: float):
    """
    Runs adversarial in-processing debiasing based on the provided fairness_weight slider value.
    """
    # Translate fairness_weight (0.0 to 1.0) into Fairlearn's difference_bound
    # At weight=1.0 -> bound=0.01 (very strict fairness)
    # At weight=0.0 -> bound=0.21 (loose, near baseline)
    bound = 0.01 + (1 - fairness_weight) * 0.2
    constraint = DemographicParity(difference_bound=bound)

    # Initialize the mitigator wrapping our base estimator
    mitigator = ExponentiatedGradient(
        LogisticRegression(max_iter=1000),
        constraints=constraint
    )
    
    # Fit the mitigator (this does the heavy lifting of adversarial training)
    mitigator.fit(X_train, y_train, sensitive_features=s_train)

    # Predict and compute the new, fairer metrics
    y_pred_fair = mitigator.predict(X_test)
    metrics = compute_fairness_metrics(y_test, y_pred_fair, s_test)

    return mitigator, metrics