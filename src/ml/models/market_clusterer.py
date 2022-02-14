"""Market clustering model for identifying investment zones."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import logging

logger = logging.getLogger(__name__)

class MarketClusterer:
    """Cluster real estate markets to identify investment zones."""

    def __init__(self, n_clusters: int = 8, method: str = "kmeans"):
        self.n_clusters = n_clusters
        self.method = method
        self.model = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.labels_ = None
        self.cluster_profiles_: Dict = {}
        self._feature_cols: List[str] = []

    def fit_predict(self, df: pd.DataFrame, feature_cols: List[str] = None) -> np.ndarray:
        """Fit clustering model and return cluster labels."""
        self._feature_cols = feature_cols or self._select_features(df)
        X = df[self._feature_cols].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        if self.method == "kmeans":
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=20)
            self.labels_ = self.model.fit_predict(X_scaled)
        elif self.method == "dbscan":
            self.model = DBSCAN(eps=0.5, min_samples=5)
            self.labels_ = self.model.fit_predict(X_scaled)
        elif self.method == "hierarchical":
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters)
            self.labels_ = self.model.fit_predict(X_scaled)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        try:
            sil_score = silhouette_score(X_scaled, self.labels_)
            ch_score = calinski_harabasz_score(X_scaled, self.labels_)
            logger.info("Clustering metrics: silhouette=%.4f, calinski=%.2f", sil_score, ch_score)
        except Exception:
            pass
        self._build_profiles(df)
        return self.labels_

    def _select_features(self, df: pd.DataFrame) -> List[str]:
        """Auto-select features for clustering."""
        candidates = ["price_per_sqft", "size_sqft", "bedrooms", "bathrooms",
                      "price_aed", "emirate_rank", "is_prime_area"]
        return [c for c in candidates if c in df.columns]

    def _build_profiles(self, df: pd.DataFrame):
        """Build cluster profiles with statistics."""
        df_copy = df.copy()
        df_copy["cluster"] = self.labels_
        for cluster_id in sorted(df_copy["cluster"].unique()):
            cluster_data = df_copy[df_copy["cluster"] == cluster_id]
            self.cluster_profiles_[int(cluster_id)] = {
                "size": len(cluster_data),
                "pct_of_total": round(len(cluster_data) / len(df_copy) * 100, 2),
                "avg_price": round(float(cluster_data["price_aed"].mean()), 0) if "price_aed" in cluster_data else 0,
                "avg_size": round(float(cluster_data["size_sqft"].mean()), 0) if "size_sqft" in cluster_data else 0,
                "avg_price_per_sqft": round(float(cluster_data["price_per_sqft"].mean()), 0) if "price_per_sqft" in cluster_data else 0,
                "dominant_emirate": cluster_data["emirate"].mode().iloc[0] if "emirate" in cluster_data and len(cluster_data) > 0 else "unknown",
                "dominant_type": cluster_data["property_type"].mode().iloc[0] if "property_type" in cluster_data and len(cluster_data) > 0 else "unknown",
                "label": self._generate_cluster_label(cluster_data),
            }

    def _generate_cluster_label(self, cluster_data: pd.DataFrame) -> str:
        """Generate a human-readable label for a cluster."""
        avg_pps = cluster_data["price_per_sqft"].mean() if "price_per_sqft" in cluster_data else 0
        avg_size = cluster_data["size_sqft"].mean() if "size_sqft" in cluster_data else 0
        if avg_pps > 2000:
            tier = "Ultra Premium"
        elif avg_pps > 1500:
            tier = "Premium"
        elif avg_pps > 1000:
            tier = "Mid-Range"
        elif avg_pps > 500:
            tier = "Affordable"
        else:
            tier = "Budget"
        return f"{tier} ({cluster_data['emirate'].mode().iloc[0] if 'emirate' in cluster_data else 'mixed'})"

    def get_investment_zones(self, min_score: float = 0.6) -> List[Dict]:
        """Identify clusters with strong investment potential."""
        zones = []
        for cluster_id, profile in self.cluster_profiles_.items():
            score = 0
            if profile["avg_price_per_sqft"] > 1000:
                score += 0.3
            if "dubai" in profile["dominant_emirate"] or "abu_dhabi" in profile["dominant_emirate"]:
                score += 0.3
            if profile["pct_of_total"] > 5:
                score += 0.2
            if profile["size"] > 10:
                score += 0.2
            if score >= min_score:
                zones.append({
                    "cluster_id": cluster_id,
                    "label": profile["label"],
                    "investment_score": round(score, 2),
                    **profile,
                })
        return sorted(zones, key=lambda x: x["investment_score"], reverse=True)

    def predict_cluster(self, X: pd.DataFrame) -> np.ndarray:
        """Predict cluster for new data points."""
        if self.model is None:
            raise RuntimeError("Model not fitted")
        X_scaled = self.scaler.transform(X[self._feature_cols].fillna(0).values)
        return self.model.predict(X_scaled)

    def reduce_dimensions(self, X: np.ndarray) -> np.ndarray:
        """Reduce to 2D using PCA for visualization."""
        return self.pca.fit_transform(X)
