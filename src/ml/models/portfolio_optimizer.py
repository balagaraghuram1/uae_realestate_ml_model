"""Portfolio optimization for real estate investment."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """Optimize real estate investment portfolios."""

    def __init__(self, risk_aversion: float = 1.0):
        self.risk_aversion = risk_aversion
        self.optimal_weights: Optional[np.ndarray] = None

    def optimize(self, returns: pd.DataFrame, target_return: float = None) -> Dict:
        """Find optimal portfolio allocation."""
        n_assets = len(returns.columns)
        mean_returns = returns.mean().values
        cov_matrix = returns.cov().values
        if target_return:
            from scipy.optimize import minimize
            def portfolio_stats(weights):
                ret = np.dot(weights, mean_returns)
                vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = ret / vol if vol > 0 else 0
                return -sharpe
            constraints = [
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},
                {"type": "eq", "fun": lambda w: np.dot(w, mean_returns) - target_return},
            ]
            bounds = [(0, 0.4)] * n_assets
            x0 = np.ones(n_assets) / n_assets
            result = minimize(portfolio_stats, x0, method="SLSQP",
                            bounds=bounds, constraints=constraints)
            self.optimal_weights = result.x
        else:
            self.optimal_weights = np.ones(n_assets) / n_assets
        port_return = np.dot(self.optimal_weights, mean_returns)
        port_vol = np.sqrt(np.dot(self.optimal_weights.T, np.dot(cov_matrix, self.optimal_weights)))
        return {
            "weights": dict(zip(returns.columns, self.optimal_weights.round(4))),
            "expected_return": round(float(port_return), 4),
            "expected_volatility": round(float(port_vol), 4),
            "sharpe_ratio": round(float(port_return / port_vol), 4) if port_vol > 0 else 0,
        }
