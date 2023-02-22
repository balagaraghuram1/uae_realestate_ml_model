import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class EDAResult:
    shape: Tuple[int, int]
    columns: List[str]
    dtypes: Dict[str, str]
    missing_values: Dict[str, int]
    missing_pct: Dict[str, float]
    summary_stats: Dict[str, Dict[str, float]]
    correlations: Optional[pd.DataFrame] = None
    outliers: Dict[str, List[int]] = field(default_factory=dict)
    duplicate_rows: int = 0
    unique_counts: Dict[str, int] = field(default_factory=dict)


class ExploratoryAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def analyze(self) -> EDAResult:
        result = EDAResult(
            shape=self.df.shape,
            columns=list(self.df.columns),
            dtypes={col: str(dtype) for col, dtype in self.df.dtypes.items()},
            missing_values=self.df.isnull().sum().to_dict(),
            missing_pct=(self.df.isnull().sum() / len(self.df) * 100).to_dict(),
            summary_stats=self._compute_summary_stats(),
            duplicate_rows=self.df.duplicated().sum(),
            unique_counts={col: self.df[col].nunique() for col in self.df.columns},
        )

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 1:
            result.correlations = self.df[numeric_cols].corr()

        for col in numeric_cols:
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)].index.tolist()
            if outliers:
                result.outliers[col] = outliers

        return result

    def _compute_summary_stats(self) -> Dict[str, Dict[str, float]]:
        stats = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats[col] = {
                "count": int(self.df[col].count()),
                "mean": float(self.df[col].mean()),
                "std": float(self.df[col].std()),
                "min": float(self.df[col].min()),
                "q1": float(self.df[col].quantile(0.25)),
                "median": float(self.df[col].median()),
                "q3": float(self.df[col].quantile(0.75)),
                "max": float(self.df[col].max()),
                "skew": float(self.df[col].skew()),
                "kurtosis": float(self.df[col].kurtosis()),
            }
        return stats

    def detect_seasonality(self, date_col: str, value_col: str) -> Dict[str, Any]:
        if date_col not in self.df.columns or value_col not in self.df.columns:
            return {}
        ts = self.df.set_index(date_col)[value_col]
        monthly = ts.resample("ME").mean()
        monthly_diff = monthly.diff().dropna()
        return {
            "observations": len(monthly),
            "mean": float(monthly.mean()),
            "std": float(monthly.std()),
            "min": float(monthly.min()),
            "max": float(monthly.max()),
            "volatility": float(monthly_diff.std()),
        }
