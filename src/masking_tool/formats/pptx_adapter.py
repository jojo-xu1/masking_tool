from __future__ import annotations

from pathlib import Path


def read_pptx_text(path: Path) -> str:
    try:
        from pptx import Presentation
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("python-pptx is required for .pptx files") from exc
    prs = Presentation(path)
    values: list[str] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                values.append(shape.text)
    return "\n".join(values)


def write_pptx_text(source_path: Path, output_path: Path, text: str) -> None:
    try:
        from pptx import Presentation
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("python-pptx is required for .pptx files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation(source_path)
    replacements = iter(text.splitlines())
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                try:
                    shape.text = next(replacements)
                except StopIteration:
                    shape.text = ""
    prs.save(output_path)
