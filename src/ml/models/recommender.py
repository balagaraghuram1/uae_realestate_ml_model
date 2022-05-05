"""Property recommendation engine using collaborative filtering."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class PropertyRecommender:
    """Recommend properties based on user preferences and behavior."""

    def __init__(self, n_factors: int = 50):
        self.n_factors = n_factors
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.user_features: Dict = {}
        self.item_features: Dict = {}

    def fit(self, interactions: pd.DataFrame, user_col: str = "user_id",
            item_col: str = "property_id", rating_col: str = "score"):
        """Fit the recommendation model."""
        self.user_item_matrix = interactions.pivot_table(
            index=user_col, columns=item_col, values=rating_col, fill_value=0
        )
        self.similarity_matrix = cosine_similarity(self.user_item_matrix.values)
        self.user_features = {
            uid: {"avg_preference": float(row.mean()), "count": int((row > 0).sum())}
            for uid, row in self.user_item_matrix.iterrows()
        }
        logger.info("Fitted recommender: %d users, %d items",
                     self.user_item_matrix.shape[0], self.user_item_matrix.shape[1])

    def recommend_for_user(self, user_id: int, n: int = 5) -> List[Dict]:
        """Get top-N recommendations for a user."""
        if user_id not in self.user_item_matrix.index:
            return self._cold_start_recommendations(n)
        user_idx = list(self.user_item_matrix.index).index(user_id)
        user_scores = self.similarity_matrix[user_idx]
        similar_users = np.argsort(user_scores)[::-1][1:11]
        similar_items = self.user_item_matrix.iloc[similar_users].mean(axis=0)
        already_seen = self.user_item_matrix.loc[user_id]
        candidates = similar_items[already_seen == 0].sort_values(ascending=False)
        recommendations = []
        for item_id, score in candidates.head(n).items():
            recommendations.append({
                "property_id": int(item_id),
                "score": round(float(score), 4),
                "reason": "similar_users_liked",
            })
        return recommendations

    def _cold_start_recommendations(self, n: int = 5) -> List[Dict]:
        """Recommendations for new users (cold start)."""
        popular = self.user_item_matrix.sum(axis=0).sort_values(ascending=False)
        return [
            {"property_id": int(pid), "score": round(float(s), 4), "reason": "popular"}
            for pid, s in popular.head(n).items()
        ]

    def similar_properties(self, property_id: int, n: int = 5) -> List[Dict]:
        """Find properties similar to a given property."""
        if property_id not in self.user_item_matrix.columns:
            return []
        item_idx = list(self.user_item_matrix.columns).index(property_id)
        item_profiles = self.user_item_matrix.values.T
        similarities = cosine_similarity([item_profiles[item_idx]], item_profiles)[0]
        similar_indices = np.argsort(similarities)[::-1][1:n + 1]
        return [
            {
                "property_id": int(self.user_item_matrix.columns[idx]),
                "similarity": round(float(similarities[idx]), 4),
            }
            for idx in similar_indices
        ]
