"""Provider dispatcher.

`generate_quiz()` is the single entry point the rest of the app calls. It picks
a provider and delegates. Gemini stays the default so existing behaviour is
unchanged unless a caller (or the AI_PROVIDER env var) explicitly asks for Claude.
"""

import os

from .claude import generate_quiz_with_claude
from .gemini import generate_quiz_with_gemini


def generate_quiz(payload, provider=None):
    """Generate a quiz with the configured AI provider.

    provider precedence: explicit argument > AI_PROVIDER env var > "gemini".
    """
    provider = (provider or os.environ.get("AI_PROVIDER") or "gemini").strip().lower()

    if provider == "gemini":
        return generate_quiz_with_gemini(payload)
    if provider in {"claude", "anthropic"}:
        return generate_quiz_with_claude(payload)

    raise ValueError(f"Unknown AI provider '{provider}'. Use 'gemini' or 'claude'.")
