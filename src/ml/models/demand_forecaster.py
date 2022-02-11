"""Demand forecasting model using ARIMA and LSTM approaches."""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, List
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

logger = logging.getLogger(__name__)

class DemandForecaster:
    """Time series demand forecasting for UAE real estate market."""

    def __init__(self, forecast_horizon: int = 12, model_type: str = "ensemble"):
        self.forecast_horizon = forecast_horizon
        self.model_type = model_type
        self.scaler = MinMaxScaler()
        self.models = {}
        self.history: List[float] = []
        self._fitted = False

    def prepare_time_series(self, df: pd.DataFrame, date_col: str,
                           value_col: str, freq: str = "M") -> pd.Series:
        """Prepare a time series from transaction data."""
        ts = df.groupby(pd.to_datetime(df[date_col]).dt.to_period(freq))[value_col].mean()
        ts = ts.sort_index()
        ts.index = ts.index.to_timestamp()
        return ts

    def fit(self, series: pd.Series) -> Dict:
        """Fit the forecasting model."""
        self.history = series.values.tolist()
        self._fitted = True
        metrics = {}
        if self.model_type in ("arima", "ensemble"):
            metrics.update(self._fit_arima(series))
        if self.model_type in ("prophet", "ensemble"):
            metrics.update(self._fit_prophet(series))
        if self.model_type in ("lstm", "ensemble"):
            metrics.update(self._fit_lstm(series))
        logger.info("Fitted demand forecaster: %s", metrics)
        return metrics

    def _fit_arima(self, series: pd.Series) -> Dict:
        """Fit ARIMA model."""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            model = ARIMA(series.values, order=(2, 1, 2))
            fitted = model.fit()
            self.models["arima"] = fitted
            aic = fitted.aic
            bic = fitted.bic
            return {"arima_aic": round(float(aic), 2), "arima_bic": round(float(bic), 2)}
        except Exception as e:
            logger.warning("ARIMA fitting failed: %s", e)
            return {}

    def _fit_prophet(self, series: pd.Series) -> Dict:
        """Fit Prophet model."""
        try:
            from prophet import Prophet
            df = pd.DataFrame({"ds": series.index, "y": series.values})
            model = Prophet(
                yearly_seasonality=True, weekly_seasonality=False,
                daily_seasonality=False, changepoint_prior_scale=0.05,
            )
            model.fit(df)
            self.models["prophet"] = model
            return {"prophet_fitted": True}
        except Exception as e:
            logger.warning("Prophet fitting failed: %s", e)
            return {}

    def _fit_lstm(self, series: pd.Series) -> Dict:
        """Fit LSTM model using Keras."""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            data = series.values.reshape(-1, 1)
            scaled = self.scaler.fit_transform(data)
            X, y = [], []
            seq_len = min(12, len(scaled) // 3)
            for i in range(seq_len, len(scaled)):
                X.append(scaled[i - seq_len:i, 0])
                y.append(scaled[i, 0])
            X, y = np.array(X), np.array(y)
            X = X.reshape(X.shape[0], X.shape[1], 1)
            model = Sequential([
                LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(16, activation="relu"),
                Dense(1),
            ])
            model.compile(optimizer="adam", loss="mse", metrics=["mae"])
            model.fit(X, y, epochs=100, batch_size=8, validation_split=0.2, verbose=0)
            self.models["lstm"] = model
            return {"lstm_fitted": True, "lstm_sequences": len(X)}
        except Exception as e:
            logger.warning("LSTM fitting failed: %s", e)
            return {}

    def predict(self, steps: Optional[int] = None) -> np.ndarray:
        """Generate demand forecasts."""
        steps = steps or self.forecast_horizon
        forecasts = {}
        if "arima" in self.models:
            arima_fc = self.models["arima"].forecast(steps=steps)
            forecasts["arima"] = arima_fc
        if "prophet" in self.models:
            future = self.models["prophet"].make_future_dataframe(periods=steps, freq="M")
            prophet_fc = self.models["prophet"].predict(future)
            forecasts["prophet"] = prophet_fc["yhat"].tail(steps).values
        if forecasts:
            all_forecasts = list(forecasts.values())
            return np.mean(all_forecasts, axis=0)
        return np.full(steps, np.mean(self.history[-12:]))

    def evaluate(self, actual: np.ndarray, predicted: np.ndarray) -> Dict:
        """Evaluate forecast accuracy."""
        return {
            "mae": round(float(mean_absolute_error(actual, predicted)), 2),
            "rmse": round(float(np.sqrt(mean_squared_error(actual, predicted))), 2),
            "mape": round(float(np.mean(np.abs((actual - predicted) / np.clip(actual, 1, None))) * 100), 2),
        }
