"""AI integration package for the Smart Quiz Generator.

All AI-related logic lives here, isolated from the Django app (`quiz_api`):

    documents.py   -> turn an uploaded file into clean text (AI input pipeline)
    prompts.py     -> build the provider-neutral quiz-generation prompt
    validation.py  -> the shared quiz JSON schema + response validation
    gemini.py      -> Google Gemini provider
    claude.py      -> Anthropic Claude provider
    providers.py   -> generate_quiz() dispatcher that picks a provider

The public surface below is what the rest of the project should import, e.g.:

    from ai_integration import generate_quiz, extract_text_from_uploaded_file
"""

from .claude import generate_quiz_with_claude
from .documents import extract_text_from_uploaded_file
from .gemini import generate_quiz_with_gemini, parse_gemini_response
from .prompts import build_gemini_prompt, build_quiz_prompt
from .providers import generate_quiz
from .validation import (
    QUIZ_JSON_SCHEMA,
    VALID_OPTIONS,
    strip_code_fences,
    validate_generated_quiz,
)

__all__ = [
    "extract_text_from_uploaded_file",
    "build_quiz_prompt",
    "build_gemini_prompt",
    "QUIZ_JSON_SCHEMA",
    "VALID_OPTIONS",
    "strip_code_fences",
    "validate_generated_quiz",
    "parse_gemini_response",
    "generate_quiz_with_gemini",
    "generate_quiz_with_claude",
    "generate_quiz",
]
