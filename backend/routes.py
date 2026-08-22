from fastapi import APIRouter, HTTPException
from backend.agent import choose_recovery_channel

from backend.data import customers_data
from backend.models import (
    ActionResponse,
    Customer,
    PredictionResponse,
    RecoverySummaryResponse,
)
from backend.schemas import PredictionRequest
from backend.services import find_customer
from backend.utils import calculate_recovery_score, get_prediction_and_action

router = APIRouter()


@router.get("/")
def home():
    return {"message": "RevenueRecover AI backend is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/customers", response_model=dict[str, list[Customer]])
def get_customers():
    return {"customers": customers_data}


@router.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.get("/predict/{customer_id}", response_model=PredictionResponse)
def predict(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    recovery_score = calculate_recovery_score(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"],
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": customer["customer_id"],
        "failed_amount": customer["failed_amount"],
        "days_since_failure": customer["days_since_failure"],
        "failure_reason": customer["failure_reason"],
        "prediction": prediction,
        "recovery_score": recovery_score,
        "recommended_action": recommended_action,
    }


@router.post("/predict", response_model=PredictionResponse)
def predict_from_input(data: PredictionRequest):
    recovery_score = calculate_recovery_score(
        data.failed_amount,
        data.days_since_failure,
        data.failure_reason,
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": data.customer_id,
        "failed_amount": data.failed_amount,
        "days_since_failure": data.days_since_failure,
        "failure_reason": data.failure_reason,
        "prediction": prediction,
        "recovery_score": recovery_score,
        "recommended_action": recommended_action,
    }


@router.get("/recoveries/summary", response_model=RecoverySummaryResponse)
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
            customer["failure_reason"],
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
        "unlikely_recoveries": unlikely,
    }


@router.get("/actions/{customer_id}", response_model=ActionResponse)
def get_action(customer_id: str):
    customer = find_customer(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    recovery_score = calculate_recovery_score(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"],
    )
    prediction, recommended_action = get_prediction_and_action(recovery_score)

    return {
        "customer_id": customer["customer_id"],
        "prediction": prediction,
        "recommended_action": recommended_action,
        "next_step": f"Action for {customer['name']}: {recommended_action}",
    }