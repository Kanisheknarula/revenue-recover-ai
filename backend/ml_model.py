import json
from pathlib import Path

import joblib
import pandas as pd


model = joblib.load("ml/recovery_model.pkl")
model_features = joblib.load("ml/model_features.pkl")


def load_metadata():
    metadata_path = Path("ml/model_metadata.json")
    if metadata_path.exists():
        with metadata_path.open(encoding="utf-8") as metadata_file:
            return json.load(metadata_file)
    return {}


def predict_recovery_probability(failed_amount, days_since_failure, failure_reason):
    input_data = pd.DataFrame(
        [
            {
                "failed_amount": failed_amount,
                "days_since_failure": days_since_failure,
                "failure_reason": failure_reason,
            }
        ]
    )

    input_encoded = pd.get_dummies(input_data, columns=["failure_reason"])

    for feature in model_features:
        if feature not in input_encoded.columns:
            input_encoded[feature] = 0

    input_encoded = input_encoded[model_features]

    probability = model.predict_proba(input_encoded)[0][1]
    return round(float(probability), 2)


def get_model_insights():
    """Expose safe, demo-friendly model details for the Model Center view."""
    readable_names = {
        "failed_amount": "Failed amount",
        "days_since_failure": "Days since failure",
        "failure_reason_bank_declined": "Bank declined",
        "failure_reason_card_expired": "Card expired",
        "failure_reason_insufficient_funds": "Insufficient funds",
        "failure_reason_upi_failed": "UPI failed",
    }

    importances = []
    for feature, importance in zip(model_features, model.feature_importances_):
        importances.append(
            {
                "feature": readable_names.get(feature, feature.replace("_", " ").title()),
                "importance": round(float(importance), 3),
            }
        )

    metadata = load_metadata()
    return {
        "model_type": "Random Forest classifier",
        "training_data": metadata.get("training_data", "Synthetic labeled recovery scenarios"),
        "training_rows": metadata.get("training_rows", 500),
        "evaluation": metadata.get("evaluation", {}),
        "input_features": len(model_features),
        "feature_importance": sorted(
            importances,
            key=lambda item: item["importance"],
            reverse=True,
        ),
        "disclaimer": "Feature importance describes this synthetic demo model and is not a production performance guarantee.",
    }
