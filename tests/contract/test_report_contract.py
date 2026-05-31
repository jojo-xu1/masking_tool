from pathlib import Path

import pytest

from masking_tool.reporting.excel_report import ALL_COLUMNS, write_report


def test_report_contract_columns_are_required() -> None:
    assert ALL_COLUMNS == [
        "No",
        "検出語句",
        "置換提案",
        "原文または前後の文脈",
        "情報カテゴリ",
        "リスクレベル",
        "判定理由",
        "推奨対応",
    ]
    assert len(ALL_COLUMNS) == 8


def test_report_contract_writes_workbook(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "機密情報検出結果.xlsx"
    write_report(path, [], [])
    workbook = openpyxl.load_workbook(path)
    sheet = workbook["検出結果"]
    assert [cell.value for cell in sheet[1]] == ALL_COLUMNS
    assert sheet.max_column == 8
