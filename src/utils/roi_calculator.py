 """Investment ROI calculator for UAE real estate."""
from typing import Dict

def calculate_roi(purchase_price: float, annual_rental_income: float,
                  annual_expenses: float, appreciation_rate: float,
                  holding_years: int = 5, mortgage_monthly: float = 0) -> Dict:
    """Calculate comprehensive ROI for a real estate investment."""
    total_rental_income = (annual_rental_income - annual_expenses) * holding_years
    future_value = purchase_price * (1 + appreciation_rate / 100) ** holding_years
    capital_gain = future_value - purchase_price
    total_mortgage_paid = mortgage_monthly * 12 * holding_years
    total_investment = purchase_price + total_mortgage_paid
    total_return = total_rental_income + capital_gain
    roi_pct = (total_return / purchase_price * 100) if purchase_price > 0 else 0
    annual_roi = roi_pct / holding_years
    cash_on_cash = (annual_rental_income - annual_expenses - mortgage_monthly * 12) / purchase_price * 100 if purchase_price > 0 else 0
    return {
        "purchase_price": purchase_price,
        "future_value": round(future_value, 0),
        "total_rental_income": round(total_rental_income, 0),
        "capital_gain": round(capital_gain, 0),
        "total_return": round(total_return, 0),
        "total_roi_pct": round(roi_pct, 2),
        "annual_roi_pct": round(annual_roi, 2),
        "cash_on_cash_yield": round(cash_on_cash, 2),
        "payback_years": round(purchase_price / max(annual_rental_income - annual_expenses, 1), 1),
    }
