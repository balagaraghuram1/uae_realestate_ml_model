"""Data cleaning pipeline with anomaly detection and validation."""
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CleaningReport:
    """Report of all cleaning operations applied."""
    total_rows: int = 0
    removed_duplicates: int = 0
    removed_nulls: int = 0
    corrected_prices: int = 0
    corrected_sizes: int = 0
    anomalies_detected: int = 0
    anomalies_removed: int = 0
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class CleaningPipeline:
    """Comprehensive data cleaning pipeline for real estate data."""

    PRICE_PERCENTILES = (0.01, 0.99)
    SIZE_PERCENTILES = (0.01, 0.99)
    MAX_BEDROOMS = 20
    MAX_BATHROOMS = 15
    MIN_SIZE_SQFT = 100
    MAX_SIZE_SQFT = 100000
    MIN_PRICE = 10000
    MAX_PRICE = 500000000

    def __init__(self, config: Optional[Dict] = None):
        if config:
            self.PRICE_PERCENTILES = config.get("price_percentiles", self.PRICE_PERCENTILES)
            self.SIZE_PERCENTILES = config.get("size_percentiles", self.SIZE_PERCENTILES)
        self.report = CleaningReport()

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
        """Run the full cleaning pipeline."""
        self.report = CleaningReport(total_rows=len(df))
        logger.info("Starting cleaning pipeline with %d rows", len(df))
        df = self._remove_exact_duplicates(df)
        df = self._standardize_columns(df)
        df = self._clean_prices(df)
        df = self._clean_sizes(df)
        df = self._clean_bedrooms_bathrooms(df)
        df = self._clean_areas(df)
        df = self._detect_anomalies(df)
        df = self._enforce_constraints(df)
        logger.info("Cleaning complete: %d rows remaining", len(df))
        return df, self.report

    def _remove_exact_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        subset_cols = [c for c in ["title", "price_aed", "area", "bedrooms", "size_sqft"] if c in df.columns]
        df = df.drop_duplicates(subset=subset_cols, keep="first").reset_index(drop=True)
        self.report.removed_duplicates = before - len(df)
        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if "area" in df.columns:
            df["area"] = df["area"].str.strip().str.title()
        if "property_type" in df.columns:
            df["property_type"] = df["property_type"].str.lower().str.strip()
        if "emirate" in df.columns:
            df["emirate"] = df["emirate"].str.lower().str.strip()
        return df

    def _clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        if "price_aed" not in df.columns:
            return df
        df["price_aed"] = pd.to_numeric(df["price_aed"], errors="coerce")
        before_nulls = df["price_aed"].isna().sum()
        df = df.dropna(subset=["price_aed"])
        self.report.removed_nulls += before_nulls
        q_low, q_high = df["price_aed"].quantile(self.PRICE_PERCENTILES)
        outliers = ((df["price_aed"] < q_low) | (df["price_aed"] > q_high)).sum()
        self.report.anomalies_detected += outliers
        mask = (df["price_aed"] >= self.MIN_PRICE) & (df["price_aed"] <= self.MAX_PRICE)
        removed = (~mask).sum()
        self.report.anomalies_removed += removed
        df = df[mask].copy()
        self.report.corrected_prices = outliers
        return df

    def _clean_sizes(self, df: pd.DataFrame) -> pd.DataFrame:
        if "size_sqft" not in df.columns:
            return df
        df["size_sqft"] = pd.to_numeric(df["size_sqft"], errors="coerce")
        before_nulls = df["size_sqft"].isna().sum()
        df = df.dropna(subset=["size_sqft"])
        self.report.removed_nulls += before_nulls
        mask = (df["size_sqft"] >= self.MIN_SIZE_SQFT) & (df["size_sqft"] <= self.MAX_SIZE_SQFT)
        removed = (~mask).sum()
        self.report.anomalies_removed += removed
        df = df[mask].copy()
        self.report.corrected_sizes = removed
        return df

    def _clean_bedrooms_bathrooms(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, max_val in [("bedrooms", self.MAX_BEDROOMS), ("bathrooms", self.MAX_BATHROOMS)]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                outliers = (df[col] > max_val).sum()
                df.loc[df[col] > max_val, col] = max_val
                self.report.anomalies_detected += outliers
        return df

    def _clean_areas(self, df: pd.DataFrame) -> pd.DataFrame:
        if "area" in df.columns:
            df["area"] = df["area"].replace({"": np.nan, "N/A": np.nan, "Unknown": np.nan})
            nulls = df["area"].isna().sum()
            if nulls > 0:
                df = df.dropna(subset=["area"])
                self.report.removed_nulls += nulls
        return df

    def _detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect multivariate anomalies using IQR method."""
        numeric_cols = ["price_aed", "size_sqft"]
        available = [c for c in numeric_cols if c in df.columns]
        if len(available) < 2:
            return df
        for col in available:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            anomaly_mask = (df[col] < lower) | (df[col] > upper)
            count = anomaly_mask.sum()
            self.report.anomalies_detected += count
        return df

    def _enforce_constraints(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enforce business constraints."""
        if "price_per_sqft" not in df.columns and "price_aed" in df.columns and "size_sqft" in df.columns:
            df["price_per_sqft"] = (df["price_aed"] / df["size_sqft"]).round(2)
        if "price_per_sqft" in df.columns:
            pps_bounds = df["price_per_sqft"].quantile([0.01, 0.99])
            mask = (df["price_per_sqft"] >= pps_bounds.iloc[0]) & (df["price_per_sqft"] <= pps_bounds.iloc[1])
            df = df[mask].copy()
        return df
