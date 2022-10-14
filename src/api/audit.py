 """Audit logging for API operations and data changes."""
import json, logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("audit")

class AuditLogger:
    """Log all significant API operations for compliance."""

    def __init__(self):
        self.logs: list = []

    def log_operation(self, operation: str, user: str = "system",
                      details: Optional[Dict] = None, status: str = "success"):
        """Log an API operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "user": user,
            "status": status,
            "details": details or {},
        }
        self.logs.append(entry)
        logger.info("AUDIT: %s by %s [%s]", operation, user, status)
        return entry

    def get_logs(self, limit: int = 100, operation: str = None) -> list:
        """Retrieve audit logs."""
        filtered = self.logs
        if operation:
            filtered = [l for l in filtered if l["operation"] == operation]
        return filtered[-limit:]

audit = AuditLogger()
