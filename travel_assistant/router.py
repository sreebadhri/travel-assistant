"""Query routing — orchestrator decisions and agent execution."""

import time

from .agents import orchestrator, weather_agent, hotel_agent
from .config import VALID_ROUTE_PREFIXES
from .logging import audit_log
from .resilience import call_with_retry


def _invoke_orchestrator(user_input: str, chat_history: list) -> str:
    """Raw orchestrator call — separated so call_with_retry can wrap it."""
    bounded_input = f"[USER_MESSAGE_START]{user_input}[USER_MESSAGE_END]"
    result = orchestrator.invoke({"messages": chat_history + [("user", bounded_input)]})
    return result["messages"][-1].content.strip()


def route(user_input: str, chat_history: list) -> tuple[bool, str]:
    """
    Use the orchestrator to decide which agent handles the query.
    Returns (success, decision_or_error_message).
    """
    start = time.time()
    success, result = call_with_retry(_invoke_orchestrator, user_input, chat_history)
    elapsed = time.time() - start

    if not success:
        audit_log.error("route_failure", detail=result)
        return False, result

    if not any(result.startswith(prefix) for prefix in VALID_ROUTE_PREFIXES):
        audit_log.blocked("invalid_route_format", detail=result[:100])
        return True, "NONE: I can only help with travel-related queries (weather and hotels)."

    audit_log.route_decision(result, elapsed)
    return True, result


def _invoke_agent(agent, user_input: str, chat_history: list) -> str:
    """Raw agent call — separated so call_with_retry can wrap it."""
    bounded_input = f"[USER_MESSAGE_START]{user_input}[USER_MESSAGE_END]"
    result = agent.invoke({"messages": chat_history + [("user", bounded_input)]})
    return result["messages"][-1].content


def run_agent(agent, user_input: str, chat_history: list) -> tuple[bool, str]:
    """Run a specific agent and return (success, response_or_error_message)."""
    agent_name = getattr(agent, "name", "unknown")
    start = time.time()
    success, result = call_with_retry(_invoke_agent, agent, user_input, chat_history)
    elapsed = time.time() - start
    audit_log.agent_response(agent_name, elapsed, success)
    return success, result
