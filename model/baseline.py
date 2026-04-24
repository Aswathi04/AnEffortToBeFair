from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from model.metrics import compute_fairness_metrics

def train_baseline(X, y, sensitive):
    """
    Splits data, trains a standard (biased) logistic regression model, 
    and computes baseline metrics.
    """
    # 80/20 train-test split
    X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
        X, y, sensitive, test_size=0.2, random_state=42
    )

    # Train standard logistic regression
    baseline_model = LogisticRegression(max_iter=1000)
    baseline_model.fit(X_train, y_train)

    # Predict and compute metrics
    y_pred = baseline_model.predict(X_test)
    metrics = compute_fairness_metrics(y_test, y_pred, s_test)

    # We return the data splits as well so they can be passed to the debiasing engine later
    data_splits = (X_train, X_test, y_train, y_test, s_train, s_test)
    
    return baseline_model, metrics, data_splits