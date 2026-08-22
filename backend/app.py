from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RevenueRecover AI Backend")


customers_data = [
    {
        "customer_id": "cust_001",
        "name": "Amit Sharma",
        "email": "amit@example.com",
        "failed_amount": 499,
        "days_since_failure": 2,
        "failure_reason": "insufficient_funds",
        "status": "payment_failed"
    },
    {
        "customer_id": "cust_002",
        "name": "Priya Mehta",
        "email": "priya@example.com",
        "failed_amount": 999,
        "days_since_failure": 5,
        "failure_reason": "card_expired",
        "status": "payment_failed"
    },
    {
        "customer_id": "cust_003",
        "name": "Rahul Verma",
        "email": "rahul@example.com",
        "failed_amount": 1499,
        "days_since_failure": 1,
        "failure_reason": "bank_declined",
        "status": "payment_failed"
    },
    {
        "customer_id": "cust_004",
        "name": "Sneha Kapoor",
        "email": "sneha@example.com",
        "failed_amount": 299,
        "days_since_failure": 7,
        "failure_reason": "upi_failed",
        "status": "payment_failed"
    }
]


class PredictionRequest(BaseModel):
    customer_id: str
    failed_amount: float
    days_since_failure: int
    failure_reason: str


def find_customer(customer_id: str):
    for customer in customers_data:
        if customer["customer_id"] == customer_id:
            return customer
    return None


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


@app.get("/")
def home():
    return {"message": "RevenueRecover AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers")
def get_customers():
    return {"customers": customers_data}


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@app.get("/predict/{customer_id}")
def predict(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    recovery_score = calculate_recovery_score(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"]
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "email": customer["email"],
        "failed_amount": customer["failed_amount"],
        "days_since_failure": customer["days_since_failure"],
        "failure_reason": customer["failure_reason"],
        "prediction": prediction,
        "recovery_score": recovery_score,
        "recommended_action": recommended_action
    }


@app.post("/predict")
def predict_from_input(data: PredictionRequest):
    recovery_score = calculate_recovery_score(
        data.failed_amount,
        data.days_since_failure,
        data.failure_reason
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": data.customer_id,
        "failed_amount": data.failed_amount,
        "days_since_failure": data.days_since_failure,
        "failure_reason": data.failure_reason,
        "prediction": prediction,
        "recovery_score": recovery_score,
        "recommended_action": recommended_action
    }


@app.get("/recoveries/summary")
def recovery_summary():
    total_customers = len(customers_data)
    total_failed_amount = sum(customer["failed_amount"] for customer in customers_data)

    likely = 0
    possible = 0
    unlikely = 0

    for customer in customers_data:
        score = calculate_recovery_score(
            customer["failed_amount"],
            customer["days_since_failure"],
            customer["failure_reason"]
        )
        prediction, _ = get_prediction_and_action(score)

        if prediction == "recovery likely":
            likely += 1
        elif prediction == "recovery possible":
            possible += 1
        else:
            unlikely += 1

    return {
        "total_failed_customers": total_customers,
        "total_failed_amount": total_failed_amount,
        "likely_recoveries": likely,
        "possible_recoveries": possible,
        "unlikely_recoveries": unlikely
    }
    
@app.get("/actions/{customer_id}")
def get_action(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    recovery_score = calculate_recovery_score(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"]
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": customer["customer_id"],
        "prediction": prediction,
        "recommended_action": recommended_action,
        "next_step": f"Action for {customer['name']}: {recommended_action}"
    }