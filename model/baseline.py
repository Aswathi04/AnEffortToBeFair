import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from model.metrics import compute_fairness_metrics

def train_baseline(X, y, sensitive):
    """
    Splits data, scales features, trains a standard (biased) logistic regression model,
    and computes baseline metrics.
    """
    # 80/20 train-test split
    X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
        X, y, sensitive, test_size=0.2, random_state=42
    )

    # Scale features — fit on train only, apply the same transform to test.
    # Without this, real-world income (tens of thousands to millions) and
    # loan_amount sit on very different scales, which is exactly what causes
    # lbfgs to throw ConvergenceWarning and can distort coefficient magnitudes.
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns, index=X_test.index)

    # Train standard logistic regression
    baseline_model = LogisticRegression(max_iter=1000)
    baseline_model.fit(X_train, y_train)

    # Predict and compute metrics
    y_pred = baseline_model.predict(X_test)
    metrics = compute_fairness_metrics(y_test, y_pred, s_test)

    # Return the *scaled* splits plus the fitted scaler, so any downstream step
    # (e.g. debiasing) uses the exact same transform instead of re-fitting on
    # different data, which would make baseline vs. debiased results incomparable.
    data_splits = (X_train, X_test, y_train, y_test, s_train, s_test)

    return baseline_model, metrics, data_splits, scaler