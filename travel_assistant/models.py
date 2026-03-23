"""Pydantic models for tool inputs and application data.

Why Pydantic?
- Declarative: define WHAT valid data looks like, not HOW to check it
- Automatic validation with clear error messages
- JSON schema generation (used by FastAPI, LangChain tool schemas)
- Type coercion: "2026-03-23" string → Python date object automatically
- Industry standard: FastAPI, LangChain, and most modern Python APIs use it

Why not just keep hand-rolled validation?
- More code to maintain
- Inconsistent error messages
- No JSON schema → can't auto-document APIs or generate OpenAPI specs
- Doesn't compose well with FastAPI (Phase 3)
"""

import re
import unicodedata
from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


def _sanitize(text: str) -> str:
    """Strip control characters and normalize unicode."""
    text = unicodedata.normalize("NFC", text)
    return "".join(
        ch for ch in text
        if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t")
    ).strip()


class WeatherRequest(BaseModel):
    """Input schema for the get_weather tool."""

    city: str = Field(
        min_length=1,
        max_length=100,
        description="The city to get weather for.",
    )

    @field_validator("city")
    @classmethod
    def city_must_be_alphabetic(cls, v: str) -> str:
        v = _sanitize(v)
        if not re.match(r"^[a-zA-Z\s\-\.\']+$", v):
            raise ValueError(
                f"Invalid city name '{v}'. Use only letters, spaces, hyphens, and periods."
            )
        return v


class HotelSearchRequest(BaseModel):
    """Input schema for the search_hotels tool."""

    city: str = Field(min_length=1, max_length=100)
    check_in: date = Field(description="Check-in date in YYYY-MM-DD format.")
    check_out: date = Field(description="Check-out date in YYYY-MM-DD format.")

    @field_validator("city")
    @classmethod
    def city_must_be_alphabetic(cls, v: str) -> str:
        v = _sanitize(v)
        if not re.match(r"^[a-zA-Z\s\-\.\']+$", v):
            raise ValueError(
                f"Invalid city name '{v}'. Use only letters, spaces, hyphens, and periods."
            )
        return v

    @model_validator(mode="after")
    def check_out_must_be_after_check_in(self) -> "HotelSearchRequest":
        """Cross-field validation — Pydantic makes this clean with model_validator."""
        if self.check_out <= self.check_in:
            raise ValueError("Check-out date must be after check-in date.")
        return self


class HotelBookingRequest(BaseModel):
    """Input schema for the book_hotel tool."""

    hotel_name: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    check_in: date
    check_out: date

    @field_validator("city")
    @classmethod
    def city_must_be_alphabetic(cls, v: str) -> str:
        v = _sanitize(v)
        if not re.match(r"^[a-zA-Z\s\-\.\']+$", v):
            raise ValueError(
                f"Invalid city name '{v}'. Use only letters, spaces, hyphens, and periods."
            )
        return v

    @field_validator("hotel_name")
    @classmethod
    def sanitize_hotel_name(cls, v: str) -> str:
        return _sanitize(v)

    @model_validator(mode="after")
    def check_out_must_be_after_check_in(self) -> "HotelBookingRequest":
        if self.check_out <= self.check_in:
            raise ValueError("Check-out date must be after check-in date.")
        return self
