import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional, Tuple


class StatisticalAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def descriptive_stats(self, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        target = columns if columns else self.df.select_dtypes(include=[np.number]).columns.tolist()
        results = {}
        for col in target:
            data = self.df[col].dropna()
            results[col] = {
                "n": int(len(data)),
                "mean": float(np.mean(data)),
                "median": float(np.median(data)),
                "mode": float(stats.mode(data, keepdims=True).mode[0]) if len(data) > 0 else 0,
                "std": float(np.std(data, ddof=1)),
                "variance": float(np.var(data, ddof=1)),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "range": float(np.ptp(data)),
                "q1": float(np.percentile(data, 25)),
                "q3": float(np.percentile(data, 75)),
                "iqr": float(np.percentile(data, 75) - np.percentile(data, 25)),
                "skewness": float(stats.skew(data)),
                "kurtosis": float(stats.kurtosis(data)),
                "cv": float(np.std(data, ddof=1) / np.mean(data)) if np.mean(data) != 0 else 0,
            }
        return results

    def normality_test(self, column: str) -> Dict[str, Any]:
        data = self.df[column].dropna()
        if len(data) < 3:
            return {"error": "Insufficient data points"}
        stat_shapiro, p_shapiro = stats.shapiro(data)
        stat_ks, p_ks = stats.kstest(data, "norm", args=(np.mean(data), np.std(data, ddof=1)))
        return {
            "shapiro_wilk": {"statistic": float(stat_shapiro), "p_value": float(p_shapiro)},
            "kolmogorov_smirnov": {"statistic": float(stat_ks), "p_value": float(p_ks)},
            "is_normal": p_shapiro > 0.05,
            "sample_size": int(len(data)),
        }

    def correlation_analysis(
        self, columns: Optional[List[str]] = None, method: str = "pearson"
    ) -> Dict[str, Any]:
        target = columns if columns else self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(target) < 2:
            return {"error": "Need at least 2 numeric columns"}
        corr_matrix = self.df[target].corr(method=method)
        result = {"method": method, "matrix": corr_matrix.to_dict()}
        pairs = []
        for i in range(len(target)):
            for j in range(i + 1, len(target)):
                r = corr_matrix.iloc[i, j]
                _, p = stats.pearsonr(
                    self.df[target[i]].dropna(), self.df[target[j]].dropna()
                ) if method == "pearson" else (r, 0)
                pairs.append({
                    "var1": target[i],
                    "var2": target[j],
                    "correlation": float(r),
                    "p_value": float(p),
                    "strength": "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.4 else "weak",
                    "direction": "positive" if r > 0 else "negative",
                })
        result["pairs"] = pairs
        return result

    def hypothesis_test_ttest(
        self, column: str, group_col: str, group1: Any, group2: Any
    ) -> Dict[str, Any]:
        g1 = self.df[self.df[group_col] == group1][column].dropna()
        g2 = self.df[self.df[group_col] == group2][column].dropna()
        t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)
        return {
            "test": "Welch's t-test",
            "group1": {"label": group1, "n": int(len(g1)), "mean": float(g1.mean()), "std": float(g1.std())},
            "group2": {"label": group2, "n": int(len(g2)), "mean": float(g2.mean()), "std": float(g2.std())},
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "mean_difference": float(g1.mean() - g2.mean()),
        }

    def anova_test(self, column: str, group_col: str) -> Dict[str, Any]:
        groups = [group.dropna() for _, group in self.df.groupby(group_col)[column]]
        if len(groups) < 2:
            return {"error": "Need at least 2 groups"}
        f_stat, p_value = stats.f_oneway(*groups)
        return {
            "test": "One-way ANOVA",
            "groups": int(len(groups)),
            "f_statistic": float(f_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
        }

    def price_index(self, date_col: str, price_col: str, base_date: str) -> pd.Series:
        df_sorted = self.df.sort_values(date_col)
        monthly_avg = df_sorted.set_index(date_col).resample("ME")[price_col].mean()
        base_value = monthly_avg.loc[base_date] if base_date in monthly_avg.index else monthly_avg.iloc[0]
        return (monthly_avg / base_value) * 100
