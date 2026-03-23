"""Input validation and sanitization."""

import re
import unicodedata
from datetime import datetime

from .config import MAX_INPUT_LENGTH, MAX_CITY_LENGTH


class ValidationError(Exception):
    """Raised when user input or tool parameters fail validation."""
    pass


def sanitize_input(text: str) -> str:
    """Strip control characters and normalize unicode, preserving printable content."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(
        ch for ch in text
        if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t")
    )
    return text.strip()


def validate_user_input(text: str) -> str:
    """Validate and sanitize raw user input. Returns cleaned text or raises ValidationError."""
    if not text or not text.strip():
        raise ValidationError("Input cannot be empty.")
    if len(text) > MAX_INPUT_LENGTH:
        raise ValidationError(
            f"Input too long ({len(text)} chars). Maximum is {MAX_INPUT_LENGTH} characters."
        )
    cleaned = sanitize_input(text)
    if not cleaned:
        raise ValidationError("Input contains no valid characters.")
    return cleaned


def validate_city(city: str) -> str:
    """Validate a city name: alphabetic (with spaces, hyphens, periods) and reasonable length."""
    city = sanitize_input(city)
    if not city:
        raise ValidationError("City name cannot be empty.")
    if len(city) > MAX_CITY_LENGTH:
        raise ValidationError(f"City name too long (max {MAX_CITY_LENGTH} chars).")
    if not re.match(r"^[a-zA-Z\s\-\.\']+$", city):
        raise ValidationError(
            f"Invalid city name: '{city}'. Use only letters, spaces, hyphens, and periods."
        )
    return city


def validate_date(date_str: str) -> str:
    """Validate date is in YYYY-MM-DD format and is a real date."""
    date_str = sanitize_input(date_str)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValidationError(
            f"Invalid date format: '{date_str}'. Use YYYY-MM-DD."
        )
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"Invalid date: '{date_str}' is not a real date.")
    return date_str
