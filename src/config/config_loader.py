"""Hierarchical configuration loader with YAML, env vars, and defaults."""
import os, json, copy
from pathlib import Path
from typing import Any, Optional, Dict
import yaml

class ConfigLoader:
    """Load and merge configurations from multiple sources with priority."""

    DEFAULT_PRIORITY = ["defaults", "yaml", "env", "cli"]

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.path.dirname(__file__))
        self._configs: Dict[str, Any] = {}
        self._loaded = False

    def load_yaml(self, filepath: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        path = self.base_dir / filepath
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data or {}

    def load_env_overrides(self, prefix: str = "UAE_") -> Dict[str, Any]:
        """Extract configuration values from environment variables."""
        overrides = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace("__", ".")
                parts = config_key.split(".")
                current = overrides
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = self._parse_env_value(value)
        return overrides

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries, with override taking priority."""
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    def load_all(self, yaml_files: list = None, env_prefix: str = "UAE_") -> Dict[str, Any]:
        """Load and merge all configuration sources."""
        if yaml_files is None:
            yaml_files = ["configs/ml_config.yaml", "configs/data_config.yaml",
                          "configs/api_config.yaml"]
        result = {}
        for yf in yaml_files:
            try:
                yaml_data = self.load_yaml(yf)
                result = self._deep_merge(result, yaml_data)
            except FileNotFoundError:
                continue
        env_overrides = self.load_env_overrides(env_prefix)
        result = self._deep_merge(result, env_overrides)
        self._configs = result
        self._loaded = True
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot-notation."""
        if not self._loaded:
            self.load_all()
        parts = key.split(".")
        current = self._configs
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self.get(name)
