"""LangChain tools — weather and hotel operations."""

from langchain_core.tools import tool

from .validation import validate_city, validate_date, sanitize_input, ValidationError

MOCK_HOTELS = [
    {"name": "Grand Plaza Hotel", "price": 150, "rating": 4.5, "type": "Premium"},
    {"name": "City Center Inn", "price": 95, "rating": 4.0, "type": "Mid-range"},
    {"name": "Budget Stay Express", "price": 60, "rating": 3.5, "type": "Budget"},
    {"name": "Heritage Boutique Hotel", "price": 120, "rating": 4.3, "type": "Boutique"},
    {"name": "Riverside Guesthouse", "price": 45, "rating": 4.1, "type": "Guesthouse"},
]


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    city = validate_city(city)
    return f"The weather in {city} is 72°F and sunny."


@tool
def search_hotels(city: str, check_in: str, check_out: str) -> str:
    """Search for available hotels in a given city for the specified dates."""
    city = validate_city(city)
    check_in = validate_date(check_in)
    check_out = validate_date(check_out)
    hotel_lines = "\n".join(
        f"{i}. {h['name']} ({h['type']}) - ${h['price']}/night - {h['rating']}★"
        for i, h in enumerate(MOCK_HOTELS, 1)
    )
    return f"Found {len(MOCK_HOTELS)} hotels in {city} ({check_in} to {check_out}):\n{hotel_lines}"


@tool
def book_hotel(hotel_name: str, city: str, check_in: str, check_out: str) -> str:
    """Book a hotel room at the specified hotel."""
    city = validate_city(city)
    check_in = validate_date(check_in)
    check_out = validate_date(check_out)
    hotel_name = sanitize_input(hotel_name)
    if not hotel_name:
        raise ValidationError("Hotel name cannot be empty.")
    return (
        f"✅ Booking confirmed!\n"
        f"Hotel: {hotel_name}\n"
        f"Location: {city}\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n"
        f"Confirmation #: HTL-2026-{hash(hotel_name) % 10000:04d}"
    )
