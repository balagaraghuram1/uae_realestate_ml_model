 """Feature importance visualization for model interpretability."""
from typing import Dict, List

def create_feature_importance_chart(importances: Dict[str, float], top_n: int = 15) -> Dict:
    """Create feature importance chart data."""
    sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {
        "type": "horizontal_bar",
        "title": "Feature Importance",
        "features": [f[0] for f in sorted_features],
        "values": [round(f[1], 4) for f in sorted_features],
        "colors": ["#0d9488" if i < 5 else "#94a3b8" for i in range(len(sorted_features))],
    }

def create_correlation_heatmap(corr_matrix: Dict) -> Dict:
    """Create correlation heatmap chart data."""
    return {
        "type": "heatmap",
        "title": "Feature Correlation Matrix",
        "data": corr_matrix,
    }
