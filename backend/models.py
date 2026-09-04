from pydantic import BaseModel


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    failed_amount: float
    days_since_failure: int
    failure_reason: str
    status: str


class PredictionResponse(BaseModel):
    customer_id: str
    failed_amount: float
    days_since_failure: int
    failure_reason: str
    prediction: str
    recovery_score: float
    recommended_action: str
    explanation: str
    channel: str
    confidence: str
    key_factors: list[str]
    model_type: str
    data_source: str


class ActionResponse(BaseModel):
    customer_id: str
    prediction: str
    recommended_action: str
    next_step: str
    channel: str
    confidence: str


class RecoverySummaryResponse(BaseModel):
    total_failed_customers: int
    total_failed_amount: float
    likely_recoveries: int
    possible_recoveries: int
    unlikely_recoveries: int
