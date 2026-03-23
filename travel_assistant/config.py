"""Application configuration and constants."""

# Input validation
MAX_INPUT_LENGTH = 500
MAX_CITY_LENGTH = 100

# Output validation
MAX_RESPONSE_LENGTH = 2000

# Chat history
MAX_HISTORY_PAIRS = 20  # Keep last 20 user/assistant exchanges = 40 messages

# Retry configuration
MAX_RETRIES = 2
RETRY_BASE_DELAY = 1  # seconds — exponential backoff: 1s, 2s

# LLM
LLM_MODEL = "gpt-4o-mini"

# Orchestrator output format
VALID_ROUTE_PREFIXES = ("WEATHER:", "HOTEL:", "BOTH:", "NONE:")

# User-facing messages
ERROR_MESSAGES = {
    "rate_limit": "I'm experiencing high demand right now. Please try again in a moment.",
    "connection": "I'm having trouble connecting to my AI service. Please check your internet connection and try again.",
    "timeout": "The request took too long. Please try again with a simpler query.",
    "auth": "There's a configuration issue with the AI service. Please check your API key.",
    "server": "The AI service is experiencing issues. Please try again later.",
    "unknown": "Something went wrong. Please try again. If the issue persists, try a simpler query.",
}

HARMFUL_REFUSAL = (
    "I'm not able to help with that type of request. "
    "I'm a travel assistant and can help you with weather information "
    "and hotel bookings."
)

STARTUP_MESSAGE = """\
🌤️  Travel Assistant (AI-powered)

ℹ️  You are chatting with an AI assistant powered by a language model.
    Please be aware of the following:

    • Responses are AI-generated and may not always be accurate
    • Weather and hotel data is currently simulated (not real-time)
    • Booking confirmations are for demonstration only
    • Please verify important travel details independently
    • I can help with: weather queries and hotel searches/bookings

Type 'quit' to exit.
"""
