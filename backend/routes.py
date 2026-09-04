from fastapi import APIRouter, HTTPException
from backend.data import customers_data
from backend.models import (
    ActionResponse,
    Customer,
    PredictionResponse,
    RecoverySummaryResponse,
)
from backend.schemas import PredictionRequest
from backend.services import find_customer
from backend.prediction_service import build_prediction, build_recovery_playbook
from backend.ml_model import get_model_insights

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

    decision = build_prediction(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"],
    )

    return {
        "customer_id": customer["customer_id"],
        "failed_amount": customer["failed_amount"],
        "days_since_failure": customer["days_since_failure"],
        "failure_reason": customer["failure_reason"],
        **decision,
    }


@router.post("/predict", response_model=PredictionResponse)
def predict_from_input(data: PredictionRequest):
    decision = build_prediction(
        data.failed_amount,
        data.days_since_failure,
        data.failure_reason,
    )

    return {
        "customer_id": data.customer_id,
        "failed_amount": data.failed_amount,
        "days_since_failure": data.days_since_failure,
        "failure_reason": data.failure_reason,
        **decision,
    }


@router.get("/recoveries/summary", response_model=RecoverySummaryResponse)
def recovery_summary():
    total_customers = len(customers_data)
    total_failed_amount = sum(customer["failed_amount"] for customer in customers_data)

    likely = 0
    possible = 0
    unlikely = 0

    for customer in customers_data:
        decision = build_prediction(
            customer["failed_amount"],
            customer["days_since_failure"],
            customer["failure_reason"],
        )

        if decision["prediction"] == "recovery likely":
            likely += 1
        elif decision["prediction"] == "recovery possible":
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

    decision = build_prediction(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"],
    )
    return {
        "customer_id": customer["customer_id"],
        "prediction": decision["prediction"],
        "recommended_action": decision["recommended_action"],
        "channel": decision["channel"],
        "confidence": decision["confidence"],
        "next_step": f"Action for {customer['name']}: {decision['recommended_action']}",
    }


@router.get("/playbooks/{customer_id}")
def get_recovery_playbook(customer_id: str):
    customer = find_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    decision = build_prediction(
        customer["failed_amount"],
        customer["days_since_failure"],
        customer["failure_reason"],
    )
    return build_recovery_playbook(customer["name"], decision)


@router.get("/analytics/portfolio")
def portfolio_analytics():
    reason_map = {}
    outcome_map = {
        "recovery likely": 0,
        "recovery possible": 0,
        "recovery unlikely": 0,
    }
    priority_cases = []
    estimated_recoverable_amount = 0

    for customer in customers_data:
        decision = build_prediction(
            customer["failed_amount"],
            customer["days_since_failure"],
            customer["failure_reason"],
        )
        reason = customer["failure_reason"]
        reason_map.setdefault(reason, {"reason": reason, "cases": 0, "amount": 0})
        reason_map[reason]["cases"] += 1
        reason_map[reason]["amount"] += customer["failed_amount"]
        outcome_map[decision["prediction"]] += 1

        expected_recovery = round(customer["failed_amount"] * decision["recovery_score"])
        estimated_recoverable_amount += expected_recovery
        priority_cases.append(
            {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "failed_amount": customer["failed_amount"],
                "recovery_score": decision["recovery_score"],
                "expected_recovery": expected_recovery,
                "recommended_action": decision["recommended_action"],
            }
        )

    return {
        "estimated_recoverable_amount": estimated_recoverable_amount,
        "reason_breakdown": sorted(reason_map.values(), key=lambda item: item["amount"], reverse=True),
        "outcome_breakdown": [
            {"label": label, "cases": cases}
            for label, cases in outcome_map.items()
        ],
        "priority_cases": sorted(
            priority_cases,
            key=lambda item: item["expected_recovery"],
            reverse=True,
        ),
    }


@router.get("/model/insights")
def model_insights():
    return get_model_insights()
