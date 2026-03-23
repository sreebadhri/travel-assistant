"""Structured JSON logging with session tracking."""

import json
import logging
import uuid
from datetime import datetime, timezone


class StructuredLogger:
    """
    JSON-based structured logger with session tracking.

    Each session gets a unique ID so all log entries from one conversation
    can be correlated. Logs to file, not console.
    """

    def __init__(self, name: str = "travel_assistant"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.FileHandler("travel_assistant.log")
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
            self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        self.session_id = uuid.uuid4().hex[:8]

    def _log(self, level: int, event: str, **kwargs):
        """Core logging method — builds a structured JSON log entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": self.session_id,
            "event": event,
            **kwargs,
        }
        self.logger.log(level, json.dumps(entry))

    def request(self, user_input: str, input_len: int):
        """Log an incoming user request. Truncate input to avoid logging PII."""
        self._log(logging.INFO, "request",
                  input_preview=user_input[:50] + ("..." if len(user_input) > 50 else ""),
                  input_len=input_len)

    def route_decision(self, decision: str, response_time: float):
        """Log the orchestrator's routing decision."""
        route = decision.split(":")[0] if ":" in decision else "UNKNOWN"
        self._log(logging.INFO, "route", route=route, response_time_s=round(response_time, 3))

    def agent_response(self, agent_name: str, response_time: float, success: bool):
        """Log an agent's response (without the content — could contain PII)."""
        level = logging.INFO if success else logging.ERROR
        self._log(level, "agent_response",
                  agent=agent_name, success=success,
                  response_time_s=round(response_time, 3))

    def blocked(self, reason: str, detail: str = ""):
        """Log a blocked request (injection, moderation, validation)."""
        self._log(logging.WARNING, "blocked", reason=reason, detail=detail)

    def error(self, error_type: str, detail: str = ""):
        """Log a system error."""
        self._log(logging.ERROR, "error", error_type=error_type, detail=detail)

    def pii_detected(self, pii_types: list[str]):
        """Log that PII was found and redacted (log the types, NOT the data)."""
        self._log(logging.WARNING, "pii_redacted", pii_types=pii_types)


# Global logger instance — created once, used throughout the session
audit_log = StructuredLogger()
