"""Prompt injection detection and content moderation."""

import re

from .config import HARMFUL_REFUSAL

# --- Prompt Injection Detection ---

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?previous",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(a\s+)?",
    r"pretend\s+(to\s+be|you\s+are)",
    r"new\s+instructions?\s*:",
    r"system\s*prompt",
    r"reveal\s+(your\s+)?(instructions|prompt|system)",
    r"show\s+(me\s+)?(your\s+)?(instructions|prompt|system)",
    r"what\s+(are\s+)?(your\s+)?(instructions|prompt|system)",
    r"repeat\s+(your\s+)?(instructions|prompt|system)",
    r"output\s+(your\s+)?(instructions|prompt|system)",
    r"bypass\s+(safety|filter|restriction)",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"developer\s+mode",
    r"sudo\s+mode",
]

_compiled_injection_patterns = [
    re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
]


def detect_prompt_injection(text: str) -> str | None:
    """
    Scan user input for known prompt injection patterns.
    Returns the matched pattern string if found, None if clean.
    """
    for pattern in _compiled_injection_patterns:
        if pattern.search(text):
            return pattern.pattern
    return None


# --- Content Moderation ---

HARMFUL_CONTENT_PATTERNS = [
    r"\b(bomb|explosive|weapon|gun|firearm)\b",
    r"\b(hack|exploit|breach|crack)\s+(into|a|the|this)",
    r"\b(kill|murder|attack|assault|harm)\s+(a|the|someone|people|him|her)",
    r"\b(drug|narcotic)s?\s+(deal|sell|buy|make|cook)",
    r"\b(steal|robbery|burglary|theft|shoplift)",
    r"\b(fraud|scam|phishing|counterfeit)",
    r"\b(suicide|self[- ]harm)\b",
]

_compiled_harmful_patterns = [
    re.compile(pattern, re.IGNORECASE) for pattern in HARMFUL_CONTENT_PATTERNS
]

OFF_TOPIC_PATTERNS = [
    (r"\b(diagnos|medical\s+advice|symptom|prescri|medication)\b", "medical"),
    (r"\b(legal\s+advice|lawyer|lawsuit|sue\s|litigation)\b", "legal"),
    (r"\b(invest|stock|crypto|trading\s+advice|financial\s+advice)\b", "financial"),
    (r"\b(therapy|therapist|counseling|mental\s+health\s+advice)\b", "mental health"),
]

_compiled_off_topic_patterns = [
    (re.compile(pattern, re.IGNORECASE), category)
    for pattern, category in OFF_TOPIC_PATTERNS
]


def check_content_moderation(text: str) -> tuple[bool, str]:
    """
    Screen user input for harmful or off-topic content.
    Returns (is_blocked, response_message).
    """
    for pattern in _compiled_harmful_patterns:
        if pattern.search(text):
            return True, HARMFUL_REFUSAL

    for pattern, category in _compiled_off_topic_patterns:
        if pattern.search(text):
            return True, (
                f"I appreciate your question, but I'm not qualified to provide "
                f"{category} advice. Please consult a qualified {category} "
                f"professional. I can help you with weather queries and hotel bookings."
            )

    return False, ""
