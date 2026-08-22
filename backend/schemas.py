from pydantic import BaseModel


class PredictionRequest(BaseModel):
    customer_id: str
    failed_amount: float
    days_since_failure: int
    failure_reason: str