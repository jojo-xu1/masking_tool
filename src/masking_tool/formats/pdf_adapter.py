from __future__ import annotations

from pathlib import Path


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
