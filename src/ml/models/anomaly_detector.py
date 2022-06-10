"""Anomaly detection for fraudulent property listings."""
import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class PropertyAnomalyDetector:
    """Detect anomalous property listings that may indicate fraud."""

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=200, contamination=contamination,
            random_state=42, n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.feature_names: list = []

    def fit(self, df: pd.DataFrame, feature_cols: list = None):
        """Fit the anomaly detector."""
        self.feature_names = feature_cols or ["price_aed", "size_sqft", "price_per_sqft", "bedrooms"]
        available = [c for c in self.feature_names if c in df.columns]
        X = df[available].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        logger.info("Anomaly detector fitted on %d samples", len(X))

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in property listings."""
        available = [c for c in self.feature_names if c in df.columns]
        X = df[available].fillna(0).values
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        result = df.copy()
        result["is_anomaly"] = predictions == -1
        result["anomaly_score"] = scores.round(4)
        n_anomalies = (predictions == -1).sum()
        logger.info("Detected %d anomalies out of %d listings", n_anomalies, len(df))
        return result

    def explain_anomalies(self, df: pd.DataFrame, n: int = 10) -> list:
        """Explain why certain listings are flagged as anomalous."""
        detected = self.detect(df)
        anomalies = detected[detected["is_anomaly"]].sort_values("anomaly_score").head(n)
        explanations = []
        for idx, row in anomalies.iterrows():
            reasons = []
            for col in ["price_aed", "size_sqft", "price_per_sqft"]:
                if col in row:
                    mean = df[col].mean()
                    std = df[col].std()
                    if std > 0:
                        z = (row[col] - mean) / std
                        if abs(z) > 2:
                            reasons.append(f"{col} is {abs(z):.1f} std deviations from mean")
            explanations.append({
                "index": idx, "score": row["anomaly_score"],
                "reasons": reasons,
            })
        return explanations
