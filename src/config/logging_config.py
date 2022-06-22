"""Structured logging configuration for the platform."""
import logging, logging.handlers, json, sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter for production."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
        return json.dumps(log_entry)

class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    def format(self, record):
        colors = {"DEBUG": "\033[36m", "INFO": "\033[32m",
                  "WARNING": "\033[33m", "ERROR": "\033[31m"}
        color = colors.get(record.levelname, "")
        reset = "\033[0m"
        return f"{color}[{record.levelname}]{reset} {record.name}: {record.getMessage()}"


def setup_logging(level: str = "INFO", json_output: bool = False):
    """Configure logging for the platform."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    if json_output:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(HumanReadableFormatter())
    root_logger.addHandler(handler)
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log", maxBytes=10 * 1024 * 1024, backupCount=5,
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
