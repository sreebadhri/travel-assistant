"""Chat history management — sliding window with sanitization."""

from .config import MAX_HISTORY_PAIRS
from .validation import sanitize_input


def trim_chat_history(history: list, max_pairs: int = MAX_HISTORY_PAIRS) -> list:
    """
    Keep only the most recent N message pairs in chat history.
    Returns a new list (doesn't mutate the original).
    """
    max_messages = max_pairs * 2
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


def sanitize_for_history(text: str) -> str:
    """Clean text before storing in chat history."""
    return sanitize_input(text)
