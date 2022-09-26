 """Tests for model saving and loading."""
import pytest, tempfile, os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

class TestModelSerialization:
    def test_save_load_model(self):
        import joblib
        model = Ridge(alpha=1.0)
        X = np.random.rand(100, 5)
        y = np.random.rand(100)
        model.fit(X, y)
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            joblib.dump(model, f.name)
            loaded = joblib.load(f.name)
            pred_original = model.predict(X[:5])
            pred_loaded = loaded.predict(X[:5])
            np.testing.assert_array_almost_equal(pred_original, pred_loaded)
            os.unlink(f.name)

    def test_model_metadata_saving(self):
        import json, tempfile, os
        metadata = {"model_type": "Ridge", "version": "1.0", "metrics": {"r2": 0.85}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(metadata, f)
            f.seek(0)
            loaded = json.load(f)
            assert loaded["model_type"] == "Ridge"
            assert loaded["metrics"]["r2"] == 0.85
            os.unlink(f.name)
