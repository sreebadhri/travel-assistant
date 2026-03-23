"""Output validation, PII redaction, and response sanitization."""

import re

from .config import MAX_RESPONSE_LENGTH
from .logging import audit_log

PII_PATTERNS = {
    "credit_card": re.compile(
        r"\b(?:\d[ -]*?){13,16}\b"
    ),
    "ssn": re.compile(
        r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"
    ),
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
    ),
}


def redact_pii(text: str) -> tuple[str, list[str]]:
    """
    Scan text for PII patterns and redact them.
    Returns (redacted_text, list_of_pii_types_found).
    """
    found_types = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found_types.append(pii_type)
            text = pattern.sub(f"[{pii_type.upper()}_REDACTED]", text)
    return text, found_types


def validate_response(text: str) -> str:
    """
    Validate and sanitize LLM output before showing to the user.
    Applies: length cap, PII redaction, hallucination disclaimer.
    """
    if len(text) > MAX_RESPONSE_LENGTH:
        text = text[:MAX_RESPONSE_LENGTH] + "\n\n[Response truncated for safety]"

    text, pii_found = redact_pii(text)
    if pii_found:
        audit_log.pii_detected(pii_found)

    disclaimer_triggers = ["$", "/night", "confirmed", "confirmation #", "booking"]
    if any(trigger in text.lower() for trigger in disclaimer_triggers):
        text += "\n\n_Note: This information is AI-generated and may not reflect " \
                "real-time availability or pricing. Please verify independently._"

    return text
