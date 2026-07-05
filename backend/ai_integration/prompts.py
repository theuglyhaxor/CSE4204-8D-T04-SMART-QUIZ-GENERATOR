"""Prompt construction for quiz generation.

The prompt is provider-neutral — both Gemini and Claude are asked for the same
JSON shape, so the downstream validation and persistence code is identical
regardless of which model produced the quiz.
"""


def build_quiz_prompt(data):
    question_count = int(data.get("question_count", 5))
    topic = data.get("topic", "general knowledge")
    syllabus = data.get("syllabus", "")
    difficulty = data.get("difficulty", "Medium")
    instruction = data.get("instruction", "Generate clear multiple-choice questions.")

    prompt = f"""
Generate {question_count} multiple-choice quiz questions about: {topic}.
Difficulty: {difficulty}.

Additional syllabus context:
{syllabus}

Instructions:
- Use only multiple-choice questions.
- Exactly 4 options per question.
- Exactly one correct answer.
- Include a short explanation for the correct answer.
- Return valid JSON only.
- Do not include markdown fences.

Return JSON in this structure:
{{
  "title": "Quiz title",
  "questions": [
    {{
      "prompt": "Question text",
      "option_a": "Option A",
      "option_b": "Option B",
      "option_c": "Option C",
      "option_d": "Option D",
      "correct_option": "A",
      "explanation": "Short explanation"
    }}
  ]
}}
"""

    if instruction:
        prompt += f"\n\nAdditional instructions:\n{instruction}"

    return prompt


# Backwards-compatible alias. The prompt is no longer Gemini-specific, but older
# callers may still import this name.
build_gemini_prompt = build_quiz_prompt
