import re



# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?instructions",
    r"override\s+(the\s+)?system\s+prompt",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+system\s+prompt",
]



# Jailbreak patterns
JAILBREAK_PATTERNS = [
    r"\bDAN\b",
    r"do\s+anything\s+now",
    r"no\s+restrictions",
    r"without\s+restrictions",
    r"bypass\s+(all\s+)?safety",
    r"remove\s+(all\s+)?restrictions",
    r"you\s+are\s+now\s+unrestricted",
]



# PII detection

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"



# Off-topic keywords
OFF_TOPIC_PATTERNS = [
    r"\bweather\b",
    r"\btemperature\b",
    r"\bstock\s+market\b",
    r"\brecipe\b",
    r"\bmovie\b",
    r"\bsports?\b",
    r"\bfootball\b",
    r"\bcricket\b",
    r"\bpolitics?\b",
    r"\bnews\b",
]


def _matches(patterns: list[str], text: str) -> bool:
    """
    Returns True if any pattern matches the input.
    """

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def check_input(question: str) -> dict:
    """
    Validate user input before it reaches the LLM.

    Returns a structured result.
    """

    if not question or not question.strip():
        return {
            "allowed": False,
            "reason": "Empty question.",
            "sanitized_input": None,
            "pii_detected": False,
        }

    original_question = question.strip()

   
    # 1. Prompt injection
    if _matches(INJECTION_PATTERNS, original_question):

        return {
            "allowed": False,
            "reason": "Potential prompt injection detected.",
            "sanitized_input": None,
            "pii_detected": False,
        }

    
    # 2. Jailbreak
    if _matches(JAILBREAK_PATTERNS, original_question):

        return {
            "allowed": False,
            "reason": "Potential jailbreak attempt detected.",
            "sanitized_input": None,
            "pii_detected": False,
        }

    
    # 3. PII detection
    pii_detected = bool(
        re.search(
            EMAIL_PATTERN,
            original_question,
            re.IGNORECASE,
        )
    )

    # Replace email addresses before logging/sending downstream
    sanitized_question = re.sub(
        EMAIL_PATTERN,
        "[REDACTED_EMAIL]",
        original_question,
    )

  
    # 4. Off-topic detection
    if _matches(OFF_TOPIC_PATTERNS, sanitized_question):

        return {
            "allowed": False,
            "reason": "Request appears to be outside the sales-data scope.",
            "sanitized_input": None,
            "pii_detected": pii_detected,
        }

    
    # 5. Safe
    return {
        "allowed": True,
        "reason": "Input is safe.",
        "sanitized_input": sanitized_question,
        "pii_detected": pii_detected,
    }