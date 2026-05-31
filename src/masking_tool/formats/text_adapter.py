from __future__ import annotations

from pathlib import Path


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
