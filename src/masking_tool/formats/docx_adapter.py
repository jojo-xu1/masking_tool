from __future__ import annotations

from pathlib import Path


def read_docx_blocks(path: Path) -> list[str]:
    try:
        from docx import Document
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("python-docx is required for .docx files") from exc
    document = Document(path)
    blocks: list[str] = []
    blocks.extend(paragraph.text for paragraph in document.paragraphs if paragraph.text)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    blocks.append(cell.text)
    return blocks


def read_docx_text(path: Path) -> str:
    return "\n".join(read_docx_blocks(path))


def write_docx_blocks(source_path: Path, output_path: Path, blocks: list[str]) -> None:
    try:
        from docx import Document
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("python-docx is required for .docx files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = Document(source_path)
    replacements = iter(blocks)
    for paragraph in document.paragraphs:
        if paragraph.text:
            paragraph.text = next(replacements, "")
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    cell.text = next(replacements, "")
    document.save(output_path)


def write_docx_text(source_path: Path, output_path: Path, text: str) -> None:
    write_docx_blocks(source_path, output_path, text.splitlines() or [text])
