import joblib
import pandas as pd


model = joblib.load("ml/recovery_model.pkl")
model_features = joblib.load("ml/model_features.pkl")


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