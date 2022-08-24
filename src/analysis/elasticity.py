"""Price elasticity analysis for real estate markets."""
import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PriceElasticityAnalyzer:
    """Analyze price elasticity of demand in real estate markets."""

    def compute_elasticity(self, prices: np.ndarray, quantities: np.ndarray) -> Dict:
        """Compute price elasticity of demand."""
        if len(prices) < 2 or len(quantities) < 2:
            return {"elasticity": 0, "type": "insufficient_data"}
        log_prices = np.log(prices)
        log_quantities = np.log(quantities)
        slope, intercept, r_value, p_value, std_err = np.polyfit(log_prices, log_quantities, 1)
        elasticity = round(float(slope), 4)
        if abs(elasticity) > 1:
            elastic_type = "elastic"
        elif abs(elasticity) < 1:
            elastic_type = "inelastic"
        else:
            elastic_type = "unit_elastic"
        return {
            "elasticity": elasticity,
            "type": elastic_type,
            "r_squared": round(float(r_value ** 2), 4),
            "interpretation": f"{'A' if elasticity > 0 else ''} {'1%' if abs(elasticity) == 1 else f'{abs(elasticity):.1%}'} "
                            f"{'increase' if elasticity > 0 else 'decrease'} in price leads to "
                            f"{'a' if abs(elasticity) == 1 else f'a {abs(elasticity):.1%}'} "
                            f"{'increase' if elasticity > 0 else 'decrease'} in demand",
        }

    def market_impact(self, elasticity: float, price_change_pct: float) -> Dict:
        """Estimate market impact of a price change."""
        demand_change = elasticity * price_change_pct
        return {
            "price_change_pct": round(price_change_pct * 100, 2),
            "expected_demand_change_pct": round(demand_change * 100, 2),
            "revenue_impact": round((1 + price_change_pct) * (1 + demand_change) - 1, 4),
        }
