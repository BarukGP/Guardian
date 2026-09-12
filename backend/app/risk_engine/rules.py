from dataclasses import dataclass


@dataclass
class RiskResult:
    score: int
    level: str
    reasons: list[str]


def evaluate_transaction(amount: float, average_amount: float = 0) -> RiskResult:
    """Regla inicial del MVP; se reemplazará por el motor ponderado del hackathon."""
    score = 0
    reasons: list[str] = []

    if amount >= 1000:
        score += 35
        reasons.append("Monto alto")

    if average_amount > 0 and amount >= average_amount * 3:
        score += 40
        reasons.append("Monto muy superior al comportamiento habitual")

    level = "high" if score >= 60 else "medium" if score >= 30 else "low"
    return RiskResult(score=min(score, 100), level=level, reasons=reasons)
