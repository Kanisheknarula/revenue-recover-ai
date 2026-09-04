from backend.agent import choose_recovery_channel
from backend.ml_model import predict_recovery_probability
from backend.utils import get_prediction_and_action


def build_prediction(failed_amount: float, days_since_failure: int, failure_reason: str):
    """Create one consistent, explainable recovery decision for every API route."""
    recovery_score = predict_recovery_probability(
        failed_amount,
        days_since_failure,
        failure_reason,
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)
    channel = choose_recovery_channel(recommended_action)
    key_factors = build_key_factors(
        failed_amount,
        days_since_failure,
        failure_reason,
    )

    return {
        "prediction": prediction,
        "recovery_score": recovery_score,
        "recommended_action": recommended_action,
        "channel": channel,
        "confidence": confidence_label(recovery_score),
        "key_factors": key_factors,
        "explanation": build_explanation(prediction, recovery_score, key_factors),
        "model_type": "Random Forest classifier",
        "data_source": "Synthetic demo recovery data",
    }


def build_key_factors(failed_amount: float, days_since_failure: int, failure_reason: str):
    factors = []

    if failed_amount <= 500:
        factors.append("Lower failed amount improves the chance of a quick recovery.")
    elif failed_amount > 1000:
        factors.append("Higher failed amount can reduce recovery likelihood.")
    else:
        factors.append("The failed amount is in a moderate recovery range.")

    if days_since_failure <= 3:
        factors.append("The payment failure is recent, so outreach can be more effective.")
    elif days_since_failure > 7:
        factors.append("The payment has been unresolved for over a week, which adds recovery risk.")
    else:
        factors.append("The time since failure suggests a standard follow-up window.")

    reason_factors = {
        "insufficient_funds": "Insufficient-funds failures often recover after a timely reminder.",
        "upi_failed": "UPI failures can be retried through a simple digital follow-up.",
        "card_expired": "An expired card usually needs an updated payment method.",
        "bank_declined": "A bank decline may need support follow-up or another payment method.",
    }
    factors.append(reason_factors.get(failure_reason, "The failure reason is included in the model decision."))
    return factors


def confidence_label(recovery_score: float):
    distance_from_midpoint = abs(recovery_score - 0.5)
    if distance_from_midpoint >= 0.35:
        return "high"
    if distance_from_midpoint >= 0.18:
        return "medium"
    return "low"


def build_explanation(prediction: str, recovery_score: float, key_factors: list[str]):
    return (
        f"The ML model predicts '{prediction}' with a recovery probability of "
        f"{recovery_score:.0%}. Primary signal: {key_factors[0]}"
    )


def build_recovery_playbook(customer_name: str, decision: dict):
    """Return a safe, simulated outreach sequence for the dashboard."""
    action = decision["recommended_action"]
    channel = decision["channel"].replace("_", " ")

    if action == "send reminder":
        follow_up = "If no payment arrives, send one concise follow-up with a payment link."
    elif action == "send discount offer":
        follow_up = "If there is no response, offer an alternate payment method before the offer expires."
    else:
        follow_up = "Route the case to support with the failure reason and prior payment context."

    return {
        "customer_name": customer_name,
        "is_simulation": True,
        "steps": [
            {"timing": "Now", "title": action.title(), "detail": f"Prepare a {channel} recovery message for {customer_name}."},
            {"timing": "24 hours", "title": "Check response", "detail": follow_up},
            {"timing": "72 hours", "title": "Review outcome", "detail": "Re-score the case and escalate only if recovery remains unlikely."},
        ],
    }
