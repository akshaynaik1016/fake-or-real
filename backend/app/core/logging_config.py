import logging
import json
import time
from typing import Optional

class StructuredLogger:
    def __init__(self, name: str = "fake_or_real"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        operation: str,
        status: str,
        scan_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        provider: Optional[str] = None,
        extra: Optional[dict] = None
    ):
        event = {
            "timestamp": time.time(),
            "operation": operation,
            "status": status,
            "scan_id": scan_id,
            "request_id": request_id,
            "user_id": user_id,
            "duration_ms": duration_ms,
            "provider": provider,
            "metadata": extra or {}
        }
        # Redact any obvious sensitive keys from extra metadata
        sanitized = self._sanitize(event)
        self.logger.info(json.dumps(sanitized))

    def _sanitize(self, data: dict) -> dict:
        sensitive_keys = {"password", "token", "secret", "cvv", "otp", "pin", "aadhaar", "pan"}
        clean = {}
        for k, v in data.items():
            if isinstance(v, dict):
                clean[k] = self._sanitize(v)
            elif any(s in k.lower() for s in sensitive_keys):
                clean[k] = "[REDACTED]"
            else:
                clean[k] = v
        return clean

audit_logger = StructuredLogger()
