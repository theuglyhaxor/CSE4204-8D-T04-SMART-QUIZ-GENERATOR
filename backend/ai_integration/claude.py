"""Anthropic Claude provider.

Uses the official `anthropic` Python SDK and Claude's structured-output feature
(`output_config.format`) so the model is constrained to return JSON matching
QUIZ_JSON_SCHEMA. The result is then run through the same validation gate the
Gemini provider uses.

Environment variables:
    ANTHROPIC_API_KEY  (required)  API key
    CLAUDE_MODEL       (optional)  defaults to "claude-opus-4-8"
"""

import json
import os

from .prompts import build_quiz_prompt
from .validation import QUIZ_JSON_SCHEMA, strip_code_fences, validate_generated_quiz


def generate_quiz_with_claude(payload):
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    model = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")

    prompt = build_quiz_prompt(payload)
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
            # Structured outputs constrain Claude to valid JSON matching the quiz shape,
            # so no markdown-fence stripping or re-prompting is needed.
            output_config={"format": {"type": "json_schema", "schema": QUIZ_JSON_SCHEMA}},
        )
    except anthropic.APIStatusError as exc:
        raise RuntimeError(f"Claude API request failed: {exc.message}")
    except anthropic.APIError as exc:
        raise RuntimeError(f"Claude API request failed: {exc}")

    if response.stop_reason == "refusal":
        raise ValueError("Claude declined to generate this quiz.")

    text = next((block.text for block in response.content if block.type == "text"), None)
    if not text:
        raise ValueError("Claude response did not include text content.")

    return validate_generated_quiz(json.loads(strip_code_fences(text)))
