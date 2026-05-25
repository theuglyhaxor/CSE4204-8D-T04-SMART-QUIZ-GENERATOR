import io
import json
import os
from pathlib import Path
from urllib import error, parse, request

VALID_OPTIONS = {"A", "B", "C", "D"}


def extract_text_from_uploaded_file(uploaded_file):
    filename = getattr(uploaded_file, "name", "")
    suffix = Path(filename).suffix.lower()
    raw_bytes = uploaded_file.read()

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        page_count = len(reader.pages)
    elif suffix in {".txt", ".md", ".csv", ".json"}:
        text = raw_bytes.decode("utf-8", errors="replace")
        page_count = 1
    else:
        raise ValueError("Unsupported file type. Upload a PDF, TXT, MD, CSV, or JSON file.")

    cleaned_text = "\n".join(line.rstrip() for line in text.splitlines())
    if not cleaned_text.strip():
        raise ValueError("The uploaded file did not contain readable text.")

    return {
        "filename": filename,
        "text": cleaned_text,
        "page_count": page_count,
    }


def build_gemini_prompt(data):
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

    return json.loads(text)


def validate_generated_quiz(payload):
    if not isinstance(payload, dict):
        raise ValueError("Gemini response must be a JSON object.")

    title = payload.get("title")
    questions = payload.get("questions")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Gemini response must include a non-empty title.")

    if not isinstance(questions, list) or not questions:
        raise ValueError("Gemini response must include a non-empty questions list.")

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


def generate_quiz_with_gemini(payload):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    prompt = build_gemini_prompt(payload)
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
                "maxOutputTokens": 2000,
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
