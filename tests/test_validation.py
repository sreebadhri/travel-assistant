"""Tests for validation.py — input validation and sanitization.

Test pyramid principle: these are UNIT tests — they test one function
in isolation, with no external dependencies (no LLM, no network, no DB).
Fast to run, easy to debug, should make up the bulk of your test suite.

Interview Q: "What's the test pyramid?"
A: A model for balancing test types. Bottom (most tests): unit tests —
   fast, isolated, test one function. Middle: integration tests — test
   multiple components working together. Top (fewest): end-to-end tests —
   test the full system. As you go up, tests get slower and more expensive.
   The mistake most teams make is inverting it (too many slow E2E tests).
"""

import pytest

from travel_assistant.validation import (
    sanitize_input,
    validate_user_input,
    validate_city,
    validate_date,
    ValidationError,
)


# --- sanitize_input ---

class TestSanitizeInput:
    def test_strips_leading_trailing_whitespace(self):
        assert sanitize_input("  hello  ") == "hello"

    def test_removes_control_characters(self):
        # \x00 is a null byte (control character) — common in injection attacks
        assert sanitize_input("hello\x00world") == "helloworld"

    def test_preserves_newlines_and_tabs(self):
        assert sanitize_input("line1\nline2") == "line1\nline2"
        assert sanitize_input("col1\tcol2") == "col1\tcol2"

    def test_normalizes_unicode(self):
        # NFC normalization: composed vs decomposed unicode should be equal
        composed = "\u00e9"       # é as single codepoint
        decomposed = "e\u0301"   # é as e + combining accent
        assert sanitize_input(decomposed) == composed

    def test_returns_empty_string_for_whitespace_only(self):
        assert sanitize_input("   ") == ""


# --- validate_user_input ---

class TestValidateUserInput:
    def test_accepts_valid_input(self):
        assert validate_user_input("What's the weather in Paris?") == \
               "What's the weather in Paris?"

    def test_raises_on_empty_string(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_user_input("")

    def test_raises_on_whitespace_only(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_user_input("   ")

    def test_raises_on_input_too_long(self):
        with pytest.raises(ValidationError, match="too long"):
            validate_user_input("a" * 501)

    def test_accepts_exactly_max_length(self):
        result = validate_user_input("a" * 500)
        assert len(result) == 500

    def test_strips_and_returns_clean_input(self):
        assert validate_user_input("  hello  ") == "hello"


# --- validate_city ---

class TestValidateCity:
    def test_accepts_simple_city(self):
        assert validate_city("Paris") == "Paris"

    def test_accepts_city_with_spaces(self):
        assert validate_city("New York") == "New York"

    def test_accepts_city_with_hyphen(self):
        assert validate_city("Saint-Denis") == "Saint-Denis"

    def test_accepts_city_with_period(self):
        assert validate_city("St. Louis") == "St. Louis"

    def test_raises_on_empty(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_city("")

    def test_raises_on_numbers(self):
        with pytest.raises(ValidationError, match="Invalid city name"):
            validate_city("New York 123")

    def test_raises_on_sql_injection_attempt(self):
        with pytest.raises(ValidationError, match="Invalid city name"):
            validate_city("'; DROP TABLE hotels;--")

    def test_raises_on_too_long(self):
        with pytest.raises(ValidationError, match="too long"):
            validate_city("A" * 101)


# --- validate_date ---

class TestValidateDate:
    def test_accepts_valid_date(self):
        assert validate_date("2026-06-15") == "2026-06-15"

    def test_raises_on_wrong_format(self):
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_date("15/06/2026")

    def test_raises_on_american_format(self):
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_date("06-15-2026")

    def test_raises_on_invalid_date(self):
        # Feb 30 doesn't exist
        with pytest.raises(ValidationError, match="not a real date"):
            validate_date("2026-02-30")

    def test_raises_on_invalid_month(self):
        with pytest.raises(ValidationError, match="not a real date"):
            validate_date("2026-13-01")

    def test_raises_on_empty(self):
        with pytest.raises(ValidationError):
            validate_date("")
