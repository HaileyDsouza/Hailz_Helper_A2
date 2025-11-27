import re

# Simple prompt-injection and to check for unsafe input
Bad_words = [
    "starve",
    "stop eating",
    "purge",
    "throw up",
    "self harm",
    "hurt myself",
    "kill myself",
    "dangerous diet",
    "fasting for days",
    "ignore previous instructions",
    "system prompt",
    "jailbreak"
]

def is_safe_input(text: str) -> bool:
    """
    Returns False if the input looks unsafe.
    Otherwise True.
    """

    if not text or text.strip() == "":
        return False

    lower = text.lower()

    for pattern in Bad_words:
        if re.search(pattern, lower):
            return False

    return True


