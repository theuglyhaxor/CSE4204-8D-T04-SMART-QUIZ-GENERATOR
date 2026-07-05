"""Google Gemini provider.

Talks to the Gemini `generateContent` REST endpoint using only the standard
library (no SDK dependency), then funnels the result through the shared
validation gate.

Environment variables:
    GEMINI_API_KEY   (required)  API key
    GEMINI_MODEL     (optional)  defaults to "gemini-2.5-flash"
    GEMINI_TIMEOUT   (optional)  request timeout in seconds, defaults to 30
"""

import json
import os
from urllib import error, parse, request

from .prompts import build_quiz_prompt
from .validation import strip_code_fences, validate_generated_quiz


def parse_gemini_response(raw_response):
    payload = json.loads(raw_response)
    candidates = payload.get("candidates") or []

    if not candidates:
        raise ValueError("Gemini returned no candidates.")

    content = candidates[0].get("content", {})
    parts = content.get("parts") or []

    if not parts:
        raise ValueError("Gemini response did not include content parts.")

    text = parts[0].get("text")
    if not text:
        raise ValueError("Gemini response did not include text content.")

    return json.loads(strip_code_fences(text))


def generate_quiz_with_gemini(payload):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    prompt = build_quiz_prompt(payload)
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{parse.quote(model)}:generateContent?key={parse.quote(api_key)}"
    )

    request_body = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            },
        }
    ).encode("utf-8")

    req = request.Request(endpoint, data=request_body, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with request.urlopen(req, timeout=int(os.environ.get("GEMINI_TIMEOUT", "30"))) as response:
            response_text = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise RuntimeError(f"Gemini API request failed: {exc.read().decode('utf-8')}")

    return validate_generated_quiz(parse_gemini_response(response_text))
