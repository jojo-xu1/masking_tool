from pathlib import Path

import pytest

from masking_tool.reporting.excel_report import REQUIRED_COLUMNS, write_report


def test_report_display_formatting(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "機密情報検出結果.xlsx"
    write_report(path, [], [])

    workbook = openpyxl.load_workbook(path)
    sheet = workbook["検出結果"]

    assert sheet.freeze_panes == "A2"
    assert sheet.auto_filter.ref == "A1:H1"
    assert [cell.value for cell in sheet[1]] == REQUIRED_COLUMNS
    assert sheet.column_dimensions["D"].width >= 40
    assert sheet["D1"].alignment.wrap_text is True
    assert sheet["A1"].font.bold is True
