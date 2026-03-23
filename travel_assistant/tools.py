"""LangChain tools — weather and hotel operations."""

from pydantic import ValidationError as PydanticValidationError
from langchain_core.tools import tool

from .models import WeatherRequest, HotelSearchRequest, HotelBookingRequest

MOCK_HOTELS = [
    {"name": "Grand Plaza Hotel", "price": 150, "rating": 4.5, "type": "Premium"},
    {"name": "City Center Inn", "price": 95, "rating": 4.0, "type": "Mid-range"},
    {"name": "Budget Stay Express", "price": 60, "rating": 3.5, "type": "Budget"},
    {"name": "Heritage Boutique Hotel", "price": 120, "rating": 4.3, "type": "Boutique"},
    {"name": "Riverside Guesthouse", "price": 45, "rating": 4.1, "type": "Guesthouse"},
]


def _pydantic_error_to_str(e: PydanticValidationError) -> str:
    """Convert Pydantic's validation error into a single readable string."""
    return "; ".join(err["msg"] for err in e.errors())


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    try:
        req = WeatherRequest(city=city)
    except PydanticValidationError as e:
        return f"Invalid input: {_pydantic_error_to_str(e)}"
    return f"The weather in {req.city} is 72°F and sunny."


@tool
def search_hotels(city: str, check_in: str, check_out: str) -> str:
    """Search for available hotels in a given city for the specified dates."""
    try:
        req = HotelSearchRequest(city=city, check_in=check_in, check_out=check_out)
    except PydanticValidationError as e:
        return f"Invalid input: {_pydantic_error_to_str(e)}"
    hotel_lines = "\n".join(
        f"{i}. {h['name']} ({h['type']}) - ${h['price']}/night - {h['rating']}★"
        for i, h in enumerate(MOCK_HOTELS, 1)
    )
    return (
        f"Found {len(MOCK_HOTELS)} hotels in {req.city} "
        f"({req.check_in} to {req.check_out}):\n{hotel_lines}"
    )


@tool
def book_hotel(hotel_name: str, city: str, check_in: str, check_out: str) -> str:
    """Book a hotel room at the specified hotel."""
    try:
        req = HotelBookingRequest(
            hotel_name=hotel_name, city=city,
            check_in=check_in, check_out=check_out,
        )
    except PydanticValidationError as e:
        return f"Invalid input: {_pydantic_error_to_str(e)}"
    return (
        f"✅ Booking confirmed!\n"
        f"Hotel: {req.hotel_name}\n"
        f"Location: {req.city}\n"
        f"Check-in: {req.check_in}\n"
        f"Check-out: {req.check_out}\n"
        f"Confirmation #: HTL-2026-{hash(req.hotel_name) % 10000:04d}"
    )
