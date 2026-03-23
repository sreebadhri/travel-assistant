"""Tests for output.py — PII redaction and response validation."""

import pytest

from travel_assistant.output import redact_pii, validate_response
from travel_assistant.config import MAX_RESPONSE_LENGTH


# --- redact_pii ---

class TestRedactPii:
    def test_clean_text_unchanged(self):
        text, found = redact_pii("The weather in Paris is sunny.")
        assert text == "The weather in Paris is sunny."
        assert found == []

    def test_redacts_email(self):
        text, found = redact_pii("Contact us at user@example.com for help")
        assert "user@example.com" not in text
        assert "EMAIL_REDACTED" in text
        assert "email" in found

    def test_redacts_credit_card(self):
        text, found = redact_pii("Your card 4532-1234-5678-9012 was charged")
        assert "4532-1234-5678-9012" not in text
        assert "CREDIT_CARD_REDACTED" in text
        assert "credit_card" in found

    def test_redacts_ssn(self):
        text, found = redact_pii("SSN: 123-45-6789")
        assert "123-45-6789" not in text
        assert "SSN_REDACTED" in text
        assert "ssn" in found

    def test_redacts_multiple_pii_types(self):
        text, found = redact_pii("Email: joe@test.com, SSN: 123-45-6789")
        assert "joe@test.com" not in text
        assert "123-45-6789" not in text
        assert len(found) == 2


# --- validate_response ---

class TestValidateResponse:
    def test_short_response_unchanged(self):
        text = "The weather in Paris is 72°F and sunny."
        result = validate_response(text)
        assert text in result  # may have disclaimer appended

    def test_truncates_long_response(self):
        long_text = "a" * (MAX_RESPONSE_LENGTH + 100)
        result = validate_response(long_text)
        assert "truncated" in result.lower()
        assert len(result) <= MAX_RESPONSE_LENGTH + 50  # some slack for the truncation message

    def test_appends_disclaimer_for_price(self):
        result = validate_response("Hotel costs $150/night")
        assert "AI-generated" in result or "verify" in result.lower()

    def test_appends_disclaimer_for_booking_confirmation(self):
        result = validate_response("Booking confirmed! Confirmation #: HTL-2026-1234")
        assert "verify" in result.lower()

    def test_redacts_pii_in_response(self):
        result = validate_response("Your email user@example.com has been noted")
        assert "user@example.com" not in result
        assert "EMAIL_REDACTED" in result
