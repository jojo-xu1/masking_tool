from __future__ import annotations

from pathlib import Path


def read_xlsx_text(path: Path) -> str:
    try:
        from openpyxl import load_workbook
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("openpyxl is required for .xlsx files") from exc
    workbook = load_workbook(path)
    values: list[str] = []
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    values.append(cell.value)
    return "\n".join(values)


def write_xlsx_text(source_path: Path, output_path: Path, text: str) -> None:
    try:
        from openpyxl import load_workbook
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("openpyxl is required for .xlsx files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(source_path)
    replacements = iter(text.splitlines())
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    try:
                        cell.value = next(replacements)
                    except StopIteration:
                        cell.value = ""
    workbook.save(output_path)
