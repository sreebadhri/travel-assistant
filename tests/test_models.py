"""Tests for models.py — Pydantic schema validation.

These tests verify the Pydantic models enforce the right constraints
and that type coercion works as expected (strings → date objects).
"""

from datetime import date

import pytest
from pydantic import ValidationError

from travel_assistant.models import (
    WeatherRequest,
    HotelSearchRequest,
    HotelBookingRequest,
)


# --- WeatherRequest ---

class TestWeatherRequest:
    def test_accepts_valid_city(self):
        r = WeatherRequest(city="Tokyo")
        assert r.city == "Tokyo"

    def test_accepts_city_with_spaces(self):
        r = WeatherRequest(city="New York")
        assert r.city == "New York"

    def test_rejects_city_with_numbers(self):
        with pytest.raises(ValidationError):
            WeatherRequest(city="New York 2")

    def test_rejects_empty_city(self):
        with pytest.raises(ValidationError):
            WeatherRequest(city="")

    def test_rejects_city_over_max_length(self):
        with pytest.raises(ValidationError):
            WeatherRequest(city="A" * 101)


# --- HotelSearchRequest ---

class TestHotelSearchRequest:
    def test_accepts_valid_request(self):
        r = HotelSearchRequest(
            city="London",
            check_in="2026-07-01",
            check_out="2026-07-05",
        )
        assert r.city == "London"
        # Pydantic coerces strings to date objects
        assert r.check_in == date(2026, 7, 1)
        assert r.check_out == date(2026, 7, 5)

    def test_coerces_string_dates(self):
        """Pydantic should convert '2026-07-01' string to a date object automatically."""
        r = HotelSearchRequest(
            city="Paris", check_in="2026-07-01", check_out="2026-07-07"
        )
        assert isinstance(r.check_in, date)
        assert isinstance(r.check_out, date)

    def test_rejects_checkout_before_checkin(self):
        with pytest.raises(ValidationError, match="after check-in"):
            HotelSearchRequest(
                city="Paris", check_in="2026-07-10", check_out="2026-07-05"
            )

    def test_rejects_checkout_same_as_checkin(self):
        with pytest.raises(ValidationError, match="after check-in"):
            HotelSearchRequest(
                city="Paris", check_in="2026-07-05", check_out="2026-07-05"
            )

    def test_rejects_invalid_date_format(self):
        with pytest.raises(ValidationError):
            HotelSearchRequest(
                city="Paris", check_in="01/07/2026", check_out="2026-07-05"
            )

    def test_rejects_invalid_city(self):
        with pytest.raises(ValidationError):
            HotelSearchRequest(
                city="Paris123", check_in="2026-07-01", check_out="2026-07-05"
            )


# --- HotelBookingRequest ---

class TestHotelBookingRequest:
    def test_accepts_valid_booking(self):
        r = HotelBookingRequest(
            hotel_name="Grand Plaza Hotel",
            city="Rome",
            check_in="2026-08-01",
            check_out="2026-08-05",
        )
        assert r.hotel_name == "Grand Plaza Hotel"
        assert r.city == "Rome"

    def test_rejects_empty_hotel_name(self):
        with pytest.raises(ValidationError):
            HotelBookingRequest(
                hotel_name="",
                city="Rome",
                check_in="2026-08-01",
                check_out="2026-08-05",
            )

    def test_rejects_checkout_before_checkin(self):
        with pytest.raises(ValidationError, match="after check-in"):
            HotelBookingRequest(
                hotel_name="Grand Plaza",
                city="Rome",
                check_in="2026-08-10",
                check_out="2026-08-05",
            )

    def test_sanitizes_hotel_name_control_chars(self):
        """Control characters in hotel name should be stripped."""
        r = HotelBookingRequest(
            hotel_name="Grand Plaza\x00Hotel",
            city="Rome",
            check_in="2026-08-01",
            check_out="2026-08-05",
        )
        assert "\x00" not in r.hotel_name
