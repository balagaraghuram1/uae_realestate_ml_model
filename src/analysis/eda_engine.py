"""Automated exploratory data analysis engine."""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from scipy import stats

logger = logging.getLogger(__name__)

class EDAEngine:
    """Automated EDA with statistical summaries and distribution analysis."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    def summary_statistics(self) -> Dict:
        """Generate comprehensive summary statistics."""
        stats_dict = {
            "shape": self.df.shape,
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "missing_values": self.df.isnull().sum().to_dict(),
            "missing_pct": (self.df.isnull().mean() * 100).round(2).to_dict(),
            "dtypes": self.df.dtypes.astype(str).to_dict(),
            "unique_counts": {col: self.df[col].nunique() for col in self.df.columns},
        }
        if self.numeric_cols:
            stats_dict["numeric_summary"] = {}
            for col in self.numeric_cols:
                s = self.df[col].dropna()
                if len(s) == 0:
                    continue
                stats_dict["numeric_summary"][col] = {
                    "mean": round(float(s.mean()), 2),
                    "std": round(float(s.std()), 2),
                    "min": round(float(s.min()), 2),
                    "q1": round(float(s.quantile(0.25)), 2),
                    "median": round(float(s.median()), 2),
                    "q3": round(float(s.quantile(0.75)), 2),
                    "max": round(float(s.max()), 2),
                    "skewness": round(float(s.skew()), 4),
                    "kurtosis": round(float(s.kurtosis()), 4),
                    "iqr": round(float(s.quantile(0.75) - s.quantile(0.25)), 2),
                    "cv": round(float(s.std() / s.mean()), 4) if s.mean() != 0 else None,
                }
        return stats_dict

    def distribution_analysis(self) -> Dict:
        """Analyze distributions of numeric columns."""
        results = {}
        for col in self.numeric_cols:
            s = self.df[col].dropna()
            if len(s) < 8:
                continue
            stat, p_value = stats.normaltest(s)
            shapiro_stat, shapiro_p = stats.shapiro(s.sample(min(5000, len(s)), random_state=42))
            results[col] = {
                "normality_test_p_value": round(float(p_value), 6),
                "is_normal": p_value > 0.05,
                "shapiro_p_value": round(float(shapiro_p), 6),
                "skewness": round(float(s.skew()), 4),
                "kurtosis": round(float(s.kurtosis()), 4),
                "suggested_transform": self._suggest_transform(s),
            }
        return results

    def _suggest_transform(self, series: pd.Series) -> str:
        """Suggest a data transformation based on distribution shape."""
        skew = abs(series.skew())
        if skew < 0.5:
            return "none"
        elif series.skew() > 1:
            return "log"
        elif series.skew() < -1:
            return "sqrt"
        elif skew < 1:
            return "boxcox"
        return "none"

    def correlation_analysis(self, method: str = "pearson", threshold: float = 0.5) -> Dict:
        """Analyze correlations between numeric variables."""
        if len(self.numeric_cols) < 2:
            return {"correlations": [], "strong_pairs": []}
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        strong_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) >= threshold:
                    strong_pairs.append({
                        "col1": corr_matrix.columns[i],
                        "col2": corr_matrix.columns[j],
                        "correlation": round(float(val), 4),
                        "strength": "strong" if abs(val) >= 0.7 else "moderate",
                    })
        return {
            "method": method,
            "matrix": corr_matrix.round(4).to_dict(),
            "strong_pairs": sorted(strong_pairs, key=lambda x: abs(x["correlation"]), reverse=True),
        }

    def outlier_analysis(self) -> Dict:
        """Detect outliers using multiple methods."""
        results = {}
        for col in self.numeric_cols:
            s = self.df[col].dropna()
            if len(s) < 10:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            iqr_outliers = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
            z_scores = np.abs(stats.zscore(s))
            z_outliers = (z_scores > 3).sum()
            results[col] = {
                "iqr_outliers": int(iqr_outliers),
                "iqr_outlier_pct": round(iqr_outliers / len(s) * 100, 2),
                "z_score_outliers": int(z_outliers),
                "z_score_outlier_pct": round(z_outliers / len(s) * 100, 2),
            }
        return results

    def generate_full_report(self) -> Dict:
        """Generate a complete EDA report."""
        logger.info("Generating full EDA report for dataset with %d rows", len(self.df))
        return {
            "summary": self.summary_statistics(),
            "distributions": self.distribution_analysis(),
            "correlations": self.correlation_analysis(),
            "outliers": self.outlier_analysis(),
        }
