from __future__ import annotations

from pathlib import Path
import re


POSTAL_HEADER_PATTERN = re.compile(r"(?:\bpostal\b|\bpostcode\b|\bzip\b|郵便番号|〒|邮政编码|邮编|郵政編碼)", re.IGNORECASE)


def read_xlsx_blocks(path: Path) -> list[str]:
    try:
        from openpyxl import load_workbook
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("openpyxl is required for .xlsx files") from exc
    workbook = load_workbook(path)
    values: list[str] = []
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value:
                    values.append(_detection_prefix_for_cell(sheet, cell) + cell.value)
    return values


def read_xlsx_text(path: Path) -> str:
    return "\n".join(read_xlsx_blocks(path))


def write_xlsx_blocks(source_path: Path, output_path: Path, blocks: list[str]) -> None:
    try:
        from openpyxl import load_workbook
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("openpyxl is required for .xlsx files") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(source_path)
    replacements = iter(blocks)
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value:
                    prefix = _detection_prefix_for_cell(sheet, cell)
                    replacement = next(replacements, "")
                    cell.value = replacement[len(prefix) :] if prefix and replacement.startswith(prefix) else replacement
    workbook.save(output_path)


def write_xlsx_text(source_path: Path, output_path: Path, text: str) -> None:
    write_xlsx_blocks(source_path, output_path, text.splitlines() or [text])


def _detection_prefix_for_cell(sheet, cell) -> str:
    label = _postal_label_for_cell(sheet, cell)
    return f"{label}: " if label else ""


def _postal_label_for_cell(sheet, cell) -> str:
    left = sheet.cell(row=cell.row, column=cell.column - 1).value if cell.column > 1 else None
    if isinstance(left, str) and POSTAL_HEADER_PATTERN.search(left):
        return left.strip()
    header = sheet.cell(row=1, column=cell.column).value if cell.row > 1 else None
    if isinstance(header, str) and POSTAL_HEADER_PATTERN.search(header):
        return header.strip()
    return ""
