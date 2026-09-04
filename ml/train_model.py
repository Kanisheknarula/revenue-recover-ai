import json
import random
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score


def generate_synthetic_data(num_rows=500, seed=42):
    random.seed(seed)
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
    report = classification_report(y_test, predictions)
    print(report)

    metadata = {
        "model_type": "Random Forest classifier",
        "training_data": "Synthetic labeled recovery scenarios",
        "training_rows": len(X_train),
        "test_rows": len(X_test),
        "input_features": X.columns.tolist(),
        "evaluation": {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 3),
            "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 3),
            "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 3),
            "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 3),
        },
    }

    joblib.dump(model, "ml/recovery_model.pkl")
    joblib.dump(X.columns.tolist(), "ml/model_features.pkl")
    with open("ml/model_metadata.json", "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)

    print("Model saved to ml/recovery_model.pkl")
    print("Feature list saved to ml/model_features.pkl")
    print("Evaluation metadata saved to ml/model_metadata.json")


if __name__ == "__main__":
    train_model()
