 """Mortgage calculation utilities for UAE property financing."""
import math
from typing import Dict

def calculate_mortgage(principal: float, annual_rate: float, years: int,
                       down_payment_pct: float = 20) -> Dict:
    """Calculate UAE mortgage details."""
    down_payment = principal * (down_payment_pct / 100)
    loan_amount = principal - down_payment
    monthly_rate = annual_rate / 100 / 12
    n_payments = years * 12
    if monthly_rate == 0:
        monthly_payment = loan_amount / n_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) /                          ((1 + monthly_rate) ** n_payments - 1)
    total_paid = monthly_payment * n_payments
    total_interest = total_paid - loan_amount
    return {
        "property_price": principal,
        "down_payment": round(down_payment, 2),
        "down_payment_pct": down_payment_pct,
        "loan_amount": round(loan_amount, 2),
        "monthly_payment": round(monthly_payment, 2),
        "annual_payment": round(monthly_payment * 12, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "interest_to_loan_ratio": round(total_interest / loan_amount, 4),
    }

def affordability_check(annual_income: float, monthly_payment: float,
                        max_income_ratio: float = 0.25) -> Dict:
    """Check mortgage affordability (UAE bank requirement: max 25% of income)."""
    max_payment = annual_income / 12 * max_income_ratio
    is_affordable = monthly_payment <= max_payment
    return {
        "annual_income": annual_income,
        "max_allowed_payment": round(max_payment, 2),
        "proposed_payment": round(monthly_payment, 2),
        "is_affordable": is_affordable,
        "utilization_pct": round(monthly_payment / max_payment * 100, 1) if max_payment > 0 else 0,
    }
