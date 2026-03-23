"""CLI entry point — the main conversation loop."""

from .agents import weather_agent, hotel_agent
from .config import STARTUP_MESSAGE
from .history import trim_chat_history, sanitize_for_history
from .logging import audit_log
from .output import validate_response
from .router import route, run_agent
from .security import detect_prompt_injection, check_content_moderation
from .validation import validate_user_input, ValidationError


def main():
    print(STARTUP_MESSAGE)

    chat_history = []

    while True:
        raw_input = input("You: ")
        if raw_input.strip().lower() in ("quit", "exit", "q"):
            print("\nThank you for using Travel Assistant. "
                  "Remember to verify all travel details independently. Goodbye!")
            break

        try:
            user_input = validate_user_input(raw_input)
        except ValidationError as e:
            audit_log.blocked("validation", detail=str(e))
            print(f"Agent: Sorry, I can't process that input. {e}\n")
            continue

        audit_log.request(user_input, len(user_input))

        injection_match = detect_prompt_injection(user_input)
        if injection_match:
            audit_log.blocked("prompt_injection", detail=injection_match)
            print("Agent: I'm sorry, but I can't process that request. "
                  "I can help you with weather queries and hotel bookings.\n")
            continue

        is_blocked, block_message = check_content_moderation(user_input)
        if is_blocked:
            audit_log.blocked("content_moderation", detail=block_message[:80])
            print(f"Agent: {block_message}\n")
            continue

        route_ok, decision = route(user_input, chat_history)
        if not route_ok:
            print(f"Agent: {decision}\n")
            continue

        if decision.startswith("WEATHER:"):
            query = decision.split(":", 1)[1].strip()
            ok, response = run_agent(weather_agent, query or user_input, chat_history)
            if not ok:
                print(f"Agent: {response}\n")
                continue
        elif decision.startswith("HOTEL:"):
            query = decision.split(":", 1)[1].strip()
            ok, response = run_agent(hotel_agent, query or user_input, chat_history)
            if not ok:
                print(f"Agent: {response}\n")
                continue
        elif decision.startswith("BOTH:"):
            query = decision.split(":", 1)[1].strip()
            w_ok, weather_resp = run_agent(weather_agent, query or user_input, chat_history)
            h_ok, hotel_resp = run_agent(hotel_agent, query or user_input, chat_history)

            if w_ok and h_ok:
                response = f"{weather_resp}\n\n---\n\n{hotel_resp}"
            elif w_ok:
                response = f"{weather_resp}\n\n---\n\n⚠️ Hotel search is temporarily unavailable."
            elif h_ok:
                response = f"⚠️ Weather service is temporarily unavailable.\n\n---\n\n{hotel_resp}"
            else:
                print(f"Agent: {weather_resp}\n")
                continue
        else:
            response = decision.split(":", 1)[1].strip() if ":" in decision else decision

        response = validate_response(response)

        print(f"Agent: {response}\n")

        chat_history.append(("user", sanitize_for_history(user_input)))
        chat_history.append(("assistant", sanitize_for_history(response)))
        chat_history = trim_chat_history(chat_history)


if __name__ == "__main__":
    main()
