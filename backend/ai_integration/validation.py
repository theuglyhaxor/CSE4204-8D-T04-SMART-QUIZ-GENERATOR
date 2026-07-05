"""The shared quiz contract: JSON schema, validation, and small helpers.

Both providers converge here. `QUIZ_JSON_SCHEMA` constrains Claude's structured
output, and `validate_generated_quiz()` is the final gate every quiz passes
through before it is persisted, no matter which model generated it.
"""

VALID_OPTIONS = {"A", "B", "C", "D"}

# JSON Schema describing the quiz shape. Used by Claude's structured outputs so the
# model is constrained to return exactly this format. The same shape is what
# validate_generated_quiz() checks, so both providers converge on one contract.
QUIZ_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "option_a": {"type": "string"},
                    "option_b": {"type": "string"},
                    "option_c": {"type": "string"},
                    "option_d": {"type": "string"},
                    "correct_option": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "explanation": {"type": "string"},
                },
                "required": [
                    "prompt",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_option",
                    "explanation",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "questions"],
    "additionalProperties": False,
}


def strip_code_fences(text):
    """Remove ```json ... ``` markdown fences some models add despite instructions."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1] if "\n" in stripped else stripped[3:]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def validate_generated_quiz(payload):
    if not isinstance(payload, dict):
        raise ValueError("AI response must be a JSON object.")

    title = payload.get("title")
    questions = payload.get("questions")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("AI response must include a non-empty title.")

    if not isinstance(questions, list) or not questions:
        raise ValueError("AI response must include a non-empty questions list.")

    validated = []

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"Question {index} must be an object.")

        prompt = question.get("prompt")
        explanation = question.get("explanation")
        correct_option = str(question.get("correct_option", "")).upper()

        option_keys = ["option_a", "option_b", "option_c", "option_d"]
        options = []

        for key in option_keys:
            option = question.get(key)
            if not isinstance(option, str) or not option.strip():
                raise ValueError(f"Question {index} is missing {key}.")
            options.append(option)

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Question {index} is missing prompt.")

        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError(f"Question {index} is missing explanation.")

        if correct_option not in VALID_OPTIONS:
            raise ValueError(f"Question {index} has an invalid correct_option.")

        validated.append(
            {
                "prompt": prompt,
                "option_a": options[0],
                "option_b": options[1],
                "option_c": options[2],
                "option_d": options[3],
                "correct_option": correct_option,
                "explanation": explanation,
            }
        )

    return {"title": title.strip(), "questions": validated}
