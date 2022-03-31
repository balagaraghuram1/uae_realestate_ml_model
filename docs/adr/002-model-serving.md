# ADR-002: Model Serving Architecture

## Status
Accepted

## Context
We need to serve multiple ML models (price prediction, demand forecasting, risk assessment, yield calculation) through a REST API with low latency and high availability.

## Decision
- Use FastAPI for the serving layer with async endpoints
- Implement model registry for versioning and A/B testing
- Use stacking ensemble for price prediction (XGBoost + LightGBM + Ridge)
- Cache predictions for identical inputs
- Health checks for all models

## Consequences
- FastAPI provides excellent performance for async workloads
- Model registry enables safe model rollouts
- Ensemble approach provides robust predictions
- Caching reduces redundant computation
