import random
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def generate_synthetic_data(num_rows=500):
    failure_reasons = [
        "insufficient_funds",
        "card_expired",
        "bank_declined",
        "upi_failed",
    ]

    rows = []

    for _ in range(num_rows):
        failed_amount = random.randint(100, 5000)
        days_since_failure = random.randint(1, 15)
        failure_reason = random.choice(failure_reasons)

        score = 0

        if failed_amount <= 500:
            score += 2
        elif failed_amount <= 1000:
            score += 1
        else:
            score -= 1

        if days_since_failure <= 3:
            score += 2
        elif days_since_failure <= 7:
            score += 1
        else:
            score -= 1

        if failure_reason == "insufficient_funds":
            score += 1
        elif failure_reason == "upi_failed":
            score += 1
        elif failure_reason == "card_expired":
            score -= 1
        elif failure_reason == "bank_declined":
            score -= 2

        recovered = 1 if score >= 2 else 0

        rows.append(
            {
                "failed_amount": failed_amount,
                "days_since_failure": days_since_failure,
                "failure_reason": failure_reason,
                "recovered": recovered,
            }
        )

    return pd.DataFrame(rows)


def train_model():
    df = generate_synthetic_data()

    df_encoded = pd.get_dummies(df, columns=["failure_reason"])

    X = df_encoded.drop("recovered", axis=1)
    y = df_encoded["recovered"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    joblib.dump(model, "ml/recovery_model.pkl")
    joblib.dump(X.columns.tolist(), "ml/model_features.pkl")

    print("Model saved to ml/recovery_model.pkl")
    print("Feature list saved to ml/model_features.pkl")


if __name__ == "__main__":
    train_model()