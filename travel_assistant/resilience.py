"""Retry logic and error handling for LLM API calls."""

import time

from openai import RateLimitError, APIConnectionError, APITimeoutError, APIStatusError

from .config import ERROR_MESSAGES, MAX_RETRIES, RETRY_BASE_DELAY


def call_with_retry(fn, *args, **kwargs) -> tuple[bool, str]:
    """
    Call a function with retry logic for transient failures.

    Uses exponential backoff. Only retries transient errors (rate limits,
    timeouts, connection issues). Does NOT retry auth errors or 4xx errors.

    Returns: (success, result_or_error_message)
    """
    last_error_message = ERROR_MESSAGES["unknown"]

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = fn(*args, **kwargs)
            return True, result
        except RateLimitError:
            last_error_message = ERROR_MESSAGES["rate_limit"]
        except APIConnectionError:
            last_error_message = ERROR_MESSAGES["connection"]
        except APITimeoutError:
            last_error_message = ERROR_MESSAGES["timeout"]
        except APIStatusError as e:
            if e.status_code in (401, 403):
                return False, ERROR_MESSAGES["auth"]
            if e.status_code >= 500:
                last_error_message = ERROR_MESSAGES["server"]
            else:
                return False, ERROR_MESSAGES["unknown"]
        except Exception:
            return False, ERROR_MESSAGES["unknown"]

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BASE_DELAY * (2 ** attempt))

    return False, last_error_message
