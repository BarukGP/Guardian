from pydantic import BaseModel


class Transaction(BaseModel):
    id: str
    account_id: str
    amount: float
    merchant: str | None = None


class RiskScore(BaseModel):
    score: int
    level: str
    reasons: list[str]
