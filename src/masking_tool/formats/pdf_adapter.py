from __future__ import annotations

from pathlib import Path
from typing import Iterable

from masking_tool.core.models import DetectionResult


def read_pdf_text(path: Path) -> str:
    try:
        import fitz
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required for .pdf files") from exc
    doc = fitz.open(path)
    text = "\n".join(page.get_text("text") for page in doc)
    if not text.strip():
        raise RuntimeError("PDF has no extractable text")
    return text


def write_pdf_text(source_path: Path, output_path: Path, text: str) -> None:
    try:
        import fitz
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required for .pdf files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(output_path)


def write_pdf_replacements(source_path: Path, output_path: Path, detections: Iterable[DetectionResult]) -> None:
    try:
        import fitz
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required for .pdf files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(source_path)
    replacement_by_text: dict[str, str] = {}
    for detection in detections:
        replacement_by_text.setdefault(detection.detected_text, detection.replacement)

    for page in doc:
        for detected_text, replacement in replacement_by_text.items():
            for rect in page.search_for(detected_text):
                page.add_redact_annot(rect, text=replacement, fill=(1, 1, 1), text_color=(0, 0, 0), fontsize=8)
        page.apply_redactions()
    doc.save(output_path)
