def calculate_recovery_score(failed_amount: float, days_since_failure: int, failure_reason: str):
    score = 0.5

    if failed_amount <= 500:
        score += 0.2
    elif failed_amount <= 1000:
        score += 0.1
    else:
        score -= 0.1

    if days_since_failure <= 2:
        score += 0.2
    elif days_since_failure <= 5:
        score += 0.1
    else:
        score -= 0.15

    if failure_reason == "insufficient_funds":
        score += 0.1
    elif failure_reason == "card_expired":
        score -= 0.05
    elif failure_reason == "bank_declined":
        score -= 0.1
    elif failure_reason == "upi_failed":
        score += 0.05

    score = max(0.0, min(score, 0.99))
    return round(score, 2)


def get_prediction_and_action(recovery_score: float):
    if recovery_score >= 0.8:
        return "recovery likely", "send reminder"
    if recovery_score >= 0.5:
        return "recovery possible", "send discount offer"
    return "recovery unlikely", "escalate to support"

def build_recovery_explanation(prediction: str, recovery_score: float):
    return f"The system predicted '{prediction}' with a recovery score of {recovery_score}."