from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_report_risk_rows_have_fill(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("alice@example.com", encoding="utf-8")
    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    workbook = openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")
    assert workbook["検出結果"]["A2"].fill.fgColor.rgb is not None
