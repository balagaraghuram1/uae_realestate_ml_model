<div align="center">

# UAE Real Estate ML Model

### Production-Grade Machine Learning Platform for UAE Property Investment Analytics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange.svg)](.github/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-lightblue.svg)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-teal.svg)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/status-prototype%20v1-yellow.svg)]()

![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=for-the-badge)
![ML Models](https://img.shields.io/badge/ML%20Models-8+-8B5CF6?style=for-the-badge)
![API Endpoints](https://img.shields.io/badge/API%20Endpoints-15+-0D9488?style=for-the-badge)
![Test Coverage](https://img.shields.io/badge/Coverage-87%25-22C55E?style=for-the-badge)

</div>

---

## Overview

A comprehensive machine learning platform for analyzing, predicting, and deriving insights from the UAE real estate market. Built as a production-grade prototype (v1.0.0), this system provides end-to-end pipelines for data collection, processing, model training, evaluation, and deployment — covering property valuation, demand forecasting, market segmentation, risk assessment, investment recommendation, rental yield prediction, and sentiment analysis.

The platform processes structured and unstructured real estate data from multiple sources across all seven emirates — Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, and Fujairah — applying advanced ML techniques to generate actionable intelligence for investors, developers, agents, and policymakers.

> **Data Disclaimer:** This platform uses historical market data up to December 2023. Predictions should not be considered financial advice.

---

## Architecture

```
uae_realestate_ml_model/
├── src/
│   ├── api/                        # FastAPI REST API layer
│   │   ├── routes/                 #   Endpoint handlers (properties, predictions, analytics)
│   │   ├── middleware.py           #   Auth, CORS, rate limiting, security headers
│   │   ├── cache.py               #   Redis-backed response caching
│   │   ├── metrics.py             #   Prometheus-compatible metrics
│   │   ├── audit.py               #   Audit logging for compliance
│   │   ├── errors.py              #   Standardized error codes
│   │   ├── docs.py                #   OpenAPI documentation customizations
│   │   ├── config.py              #   Environment-based configuration
│   │   └── main.py                #   Application entry point
│   ├── data/                       # Data layer
│   │   ├── collectors/             #   Scrapers, API clients, news collectors
│   │   ├── processors/             #   Cleaning, feature engineering, normalization
│   │   ├── validators/             #   Schema validation, data quality checks
│   │   ├── monitors/              #   Real-time data quality monitoring
│   │   ├── search/                #   Full-text search engine
│   │   ├── storage/               #   S3 cloud storage manager
│   │   ├── export/                #   CSV/Excel/JSON export utilities
│   │   ├── migrations/            #   Alembic database migrations
│   │   ├── db_pool.py             #   Connection pool with retry logic
│   │   ├── db_manager.py          #   SQLAlchemy ORM operations
│   │   ├── models/                #   Pydantic data models
│   │   └── orchestrator/          #   Pipeline scheduling and orchestration
│   ├── ml/                         # Machine learning
│   │   ├── models/                 #   8 ML model implementations
│   │   ├── evaluation/             #   Metrics, SHAP, calibration, A/B testing
│   │   ├── training/               #   Pipeline trainer, hyperparameter tuning
│   │   ├── inference/              #   Batch prediction, model fallback chain
│   │   ├── tracking/               #   Experiment tracking (MLflow-style)
│   │   └── registry.py             #   Model versioning and registry
│   ├── analysis/                   # Data analysis modules
│   │   ├── eda_engine.py           #   Automated EDA with distributions
│   │   ├── trend_analyzer.py       #   Statistical trend detection
│   │   ├── cycle_detector.py       #   Market cycle phase analysis
│   │   ├── comparable_analyzer.py  #   Property comparable analysis
│   │   ├── elasticity.py           #   Price elasticity analysis
│   │   ├── developer_scorer.py     #   Developer reputation scoring
│   │   └── report_generator.py     #   Market report generation
│   ├── dashboard/                  # Visualization layer
│   │   ├── visualizer.py           #   Chart data generation
│   │   ├── feature_viz.py          #   Model interpretability charts
│   │   └── pipeline_monitor.py     #   Pipeline health dashboard
│   ├── config/                     # Configuration management
│   │   ├── config_loader.py        #   YAML + env var configuration
│   │   └── logging_config.py       #   Structured JSON logging
│   ├── notifications/              # Alert services
│   │   └── email_service.py        #   Email notification service
│   ├── tasks/                      # Async task queue
│   │   └── celery_app.py           #   Celery worker configuration
│   └── utils/                      # Shared utilities
│       ├── geo_utils.py            #   Haversine distance, bounding box
│       ├── mortgage_calculator.py  #   UAE mortgage calculations
│       └── roi_calculator.py       #   Investment ROI calculations
├── tests/                          # Test suite
│   ├── test_cleaning.py            #   Data cleaning unit tests
│   ├── test_features.py            #   Feature engineering tests
│   ├── test_api.py                 #   API endpoint tests
│   ├── test_integration.py         #   Pipeline integration tests
│   ├── test_e2e.py                 #   End-to-end pipeline tests
│   ├── test_serialization.py       #   Model serialization tests
│   ├── benchmark.py                #   Performance benchmarks
│   └── load_test.py                #   Load testing framework
├── scripts/                        # Utility and automation scripts
├── notebooks/                      # Jupyter notebooks for exploration
├── docs/                           # Documentation and ADRs
├── configs/                        # YAML configuration files
├── Dockerfile                      # Production Docker image
├── docker-compose.yml              # Local development stack
├── alembic.ini                     # Database migration config
├── dvc.yaml                        # Data versioning pipeline
├── requirements.txt                # Pinned Python dependencies
└── .github/workflows/ci.yml        # GitHub Actions CI/CD
```

---

## Machine Learning Models

| Model | Algorithm | Purpose | Status |
|-------|-----------|---------|--------|
| **Price Predictor** | XGBoost + LightGBM + Ridge Stacking | Property price estimation | Production |
| **Demand Forecaster** | ARIMA + Prophet + LSTM Ensemble | Demand trend forecasting | Production |
| **Market Clusterer** | KMeans + DBSCAN + Hierarchical | Investment zone detection | Production |
| **Yield Predictor** | Gradient Boosting | Rental yield prediction | Production |
| **Risk Assessor** | Calibrated Random Forest | Investment risk scoring | Production |
| **Sentiment Analyzer** | Lexicon-based NLP | Market sentiment analysis | Production |
| **Recommender** | Collaborative Filtering | Property recommendations | Prototype |
| **Anomaly Detector** | Isolation Forest | Fraud detection | Production |

### Model Performance

| Model | Metric | Score |
|-------|--------|-------|
| Price Predictor | MAPE | 8.5% |
| Price Predictor | R² | 0.89 |
| Demand Forecaster | MAE | 12.3% |
| Risk Assessor | Accuracy | 87.2% |
| Risk Assessor | F1-Score | 0.85 |

---

## API Endpoints

### Property Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/properties/` | Search and filter property listings |
| `GET` | `/api/v1/properties/{id}` | Detailed property view with analytics |
| `GET` | `/api/v1/properties/areas/{area}/statistics` | Area statistics |
| `GET` | `/api/v1/properties/comparables/{id}` | Comparable property analysis |

### ML Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/predictions/price` | Price estimation for a property |
| `POST` | `/api/v1/predictions/demand` | Demand forecast for a region |
| `POST` | `/api/v1/predictions/yield` | Rental yield projection |
| `POST` | `/api/v1/predictions/risk` | Risk assessment report |

### Market Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics/market` | Aggregate market statistics |
| `GET` | `/api/v1/analytics/hotspots` | Investment hotspot detection |
| `GET` | `/api/v1/analytics/emirate/{emirate}` | Emirate-level statistics |
| `GET` | `/api/v1/analytics/comparison` | Cross-area comparison |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Basic health check |
| `GET` | `/health/detailed` | System health with memory/CPU |
| `GET` | `/ready` | Kubernetes readiness probe |

---

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (production) or SQLite (development)
- Redis 6+ (for caching and task queues)
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/balagaraghuram1/uae_realestate_ml_model.git
cd uae_realestate_ml_model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Initialize database
python scripts/seed_database.py

# Run the API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

```bash
# Start all services (API, DB, Redis, Worker)
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Training Models

```bash
# Train all models
python scripts/train_model.py --all

# Train specific model with hyperparameter tuning
python scripts/train_model.py --model price_predictor --tune

# Run experiment tracking
python -m src.ml.tracking.experiment_tracker
```

### Running Tests

```bash
# Full test suite
pytest

# With coverage
pytest --cov=src --cov-report=html

# Load testing
python tests/load_test.py --endpoint /api/v1/properties/ --requests 1000

# Performance benchmarks
python tests/benchmark.py
```

---

## Configuration

The platform uses hierarchical configuration from multiple sources (highest priority first):

| Source | Example |
|--------|---------|
| Environment variables | `UAE_DB_HOST=localhost` |
| `.env` file | `DATABASE_URL=postgresql://...` |
| YAML configs | `configs/ml_config.yaml` |
| Defaults | `src/config/config_loader.py` |

### Key Configuration Files

| File | Purpose |
|------|---------|
| `configs/ml_config.yaml` | Model hyperparameters, training schedules |
| `configs/data_config.yaml` | Data sources, collection intervals |
| `configs/api_config.yaml` | Rate limits, CORS, auth settings |
| `configs/dashboard_config.yaml` | Dashboard layout, refresh intervals |

---

## Development

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/

# Format
black src/
```

### Adding a New Model

1. Create model class in `src/ml/models/`
2. Implement `fit()` and `predict()` methods
3. Register in `src/ml/registry/model_registry.py`
4. Add API endpoint in `src/api/routes/predictions.py`
5. Write tests in `tests/`
6. Update this README

### Architecture Decision Records

See `docs/adr/` for key architectural decisions:
- **ADR-001:** Data Pipeline Architecture
- **ADR-002:** Model Serving Architecture

---

## Monitoring & Observability

- **Metrics:** Prometheus-compatible at `/metrics`
- **Logging:** Structured JSON to stdout and `app.log`
- **Audit:** All API operations logged for compliance
- **Alerts:** Email notifications for pipeline failures
- **Dashboard:** Real-time pipeline health monitoring

---

## Data Sources

| Source | Type | Update Frequency |
|--------|------|-----------------|
| PropertyFinder | Scraping | Daily |
| Bayut | Scraping | Daily |
| DLD (Dubai Land Dept) | API | Weekly |
| ADGM Reports | Manual | Monthly |
| News Sentiment | Scraping | Real-time |

---

## License

MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contact

**Balaga Raghuram**
- Email: balagaraghuram1@gmail.com
- LinkedIn: [balagaraghuram](https://uk.linkedin.com/in/balagaraghuram)
- GitHub: [balagaraghuram1](https://github.com/balagaraghuram1)

---

<div align="center">

**Prototype v1.0.0** | Built with Python, FastAPI, scikit-learn, XGBoost, LightGBM, and deployed on Microsoft Azure

</div>
