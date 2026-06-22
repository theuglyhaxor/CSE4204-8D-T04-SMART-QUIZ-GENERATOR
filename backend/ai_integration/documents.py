"""Document ingestion — convert an uploaded file into clean text.

This is the input stage of the AI pipeline: a teacher uploads a document, we
extract readable text from it, and that text can then seed quiz generation.
"""

import io
from pathlib import Path


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
