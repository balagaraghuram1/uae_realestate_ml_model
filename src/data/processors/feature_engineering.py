"""Feature engineering pipeline with automated feature generation."""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Automated feature engineering for real estate ML models."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        self._fitted = False
        self.feature_names_: List[str] = []

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform the training dataset."""
        df = df.copy()
        df = self._create_price_features(df)
        df = self._create_location_features(df)
        df = self._create_size_features(df)
        df = self._create_temporal_features(df)
        df = self._create_interaction_features(df)
        df = self._create_cluster_features(df)
        df = self._encode_categoricals(df)
        df = self._scale_numerics(df)
        self._fitted = True
        self.feature_names_ = df.columns.tolist()
        logger.info("Feature engineering complete: %d features", len(self.feature_names_))
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted encoders and scalers."""
        if not self._fitted:
            raise RuntimeError("FeatureEngineer must be fitted before transform")
        df = df.copy()
        df = self._create_price_features(df)
        df = self._create_location_features(df)
        df = self._create_size_features(df)
        df = self._create_temporal_features(df)
        df = self._create_interaction_features(df)
        df = self._encode_categoricals(df, fit=False)
        df = self._scale_numerics(df, fit=False)
        return df

    def _create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer price-based features."""
        if "price_aed" in df.columns:
            df["price_log"] = np.log1p(df["price_aed"])
            df["price_squared"] = df["price_aed"] ** 2
            df["price_bin"] = pd.cut(
                df["price_aed"],
                bins=[0, 500000, 1000000, 2000000, 5000000, 10000000, float("inf")],
                labels=["budget", "affordable", "mid", "premium", "luxury", "ultra_luxury"],
            )
        if "price_aed" in df.columns and "size_sqft" in df.columns:
            df["price_per_sqft"] = df["price_aed"] / df["size_sqft"].clip(lower=1)
            df["price_per_bedroom"] = df["price_aed"] / df["bedrooms"].clip(lower=1)
            df["price_per_bathroom"] = df["price_aed"] / df["bathrooms"].clip(lower=1)
        return df

    def _create_location_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer location-based features."""
        emirate_dubai_areas = {
            "Dubai Marina", "Palm Jumeirah", "Downtown Dubai", "JBR",
            "Business Bay", "JVC", "Dubai Hills Estate", "Dubai Creek Harbour",
            "Arabian Ranches", "Motor City", "Sports City", "Discovery Gardens",
            "Dubai Silicon Oasis", "Dubai Sports City", "Town Square",
        }
        if "area" in df.columns:
            df["is_prime_area"] = df["area"].isin(emirate_dubai_areas).astype(int)
            df["area_length"] = df["area"].str.len()
            df["area_word_count"] = df["area"].str.split().str.len()
        if "emirate" in df.columns:
            emirate_ranks = {
                "dubai": 5, "abu_dhabi": 4, "sharjah": 3,
                "ajman": 2, "ras_al_khaimah": 2, "fujairah": 1, "umm_al_quwain": 1,
            }
            df["emirate_rank"] = df["emirate"].map(emirate_ranks).fillna(1)
            df["is_dubai"] = (df["emirate"] == "dubai").astype(int)
            df["is_abu_dhabi"] = (df["emirate"] == "abu_dhabi").astype(int)
        if "latitude" in df.columns and "longitude" in df.columns:
            dubai_lat, dubai_lon = 25.2048, 55.2708
            df["dist_to_dubai_center"] = np.sqrt(
                (df["latitude"] - dubai_lat) ** 2 + (df["longitude"] - dubai_lon) ** 2
            ) * 111
        return df

    def _create_size_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer size-based features."""
        if "size_sqft" in df.columns:
            df["size_log"] = np.log1p(df["size_sqft"])
            df["size_bin"] = pd.cut(
                df["size_sqft"],
                bins=[0, 500, 1000, 1500, 2500, 5000, float("inf")],
                labels=["micro", "compact", "standard", "spacious", "large", "estate"],
            )
        if "bedrooms" in df.columns and "size_sqft" in df.columns:
            df["size_per_bedroom"] = df["size_sqft"] / df["bedrooms"].clip(lower=1)
            df["bedroom_bath_ratio"] = df["bedrooms"] / df["bathrooms"].clip(lower=1)
        if all(c in df.columns for c in ["bedrooms", "bathrooms", "parking_spaces"]):
            df["total_rooms"] = df["bedrooms"] + df["bathrooms"] + df["parking_spaces"]
        return df

    def _create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer time-based features."""
        for col in ["created_at", "transaction_date"]:
            if col in df.columns:
                dt = pd.to_datetime(df[col], errors="coerce")
                df[f"{col}_year"] = dt.dt.year
                df[f"{col}_month"] = dt.dt.month
                df[f"{col}_dayofweek"] = dt.dt.dayofweek
                df[f"{col}_quarter"] = dt.dt.quarter
                df[f"{col}_is_weekend"] = dt.dt.dayofweek.isin([5, 6]).astype(int)
        return df

    def _create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between important columns."""
        pairs = [("bedrooms", "bathrooms"), ("size_sqft", "emirate_rank"),
                 ("price_per_sqft", "is_prime_area")]
        for c1, c2 in pairs:
            if c1 in df.columns and c2 in df.columns:
                df[f"{c1}_x_{c2}"] = df[c1] * df[c2]
        return df

    def _create_cluster_features(self, df: pd.DataFrame, n_clusters: int = 8) -> pd.DataFrame:
        """Create cluster-based features using KMeans."""
        cluster_cols = [c for c in ["price_per_sqft", "size_sqft", "bedrooms"] if c in df.columns]
        if len(cluster_cols) < 2:
            return df
        X = df[cluster_cols].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=min(n_clusters, len(X)), random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(X_scaled)
        df["cluster_distance"] = np.min(kmeans.transform(X_scaled), axis=1)
        return df

    def _encode_categoricals(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Encode categorical variables."""
        cat_cols = ["property_type", "emirate"]
        for col in cat_cols:
            if col in df.columns:
                if fit:
                    le = LabelEncoder()
                    df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                    self.encoders[col] = le
                else:
                    le = self.encoders.get(col)
                    if le:
                        df[f"{col}_encoded"] = df[col].astype(str).map(
                            lambda x: le.transform([x])[0] if x in le.classes_ else -1
                        )
        if "emirate" in df.columns:
            dummies = pd.get_dummies(df["emirate"], prefix="emirate", drop_first=True)
            df = pd.concat([df, dummies], axis=1)
        return df

    def _scale_numerics(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features."""
        scale_cols = ["price_aed", "size_sqft", "bedrooms", "bathrooms"]
        available = [c for c in scale_cols if c in df.columns]
        for col in available:
            if fit:
                scaler = StandardScaler()
                df[f"{col}_scaled"] = scaler.fit_transform(df[[col]])
                self.scalers[col] = scaler
            else:
                scaler = self.scalers.get(col)
                if scaler:
                    df[f"{col}_scaled"] = scaler.transform(df[[col]])
        return df
