from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_report_uses_pre_replacement_full_line_context(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    original_line = "Contact Alice Smith at alice@example.com."
    source.write_text(original_line + "\n", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    contexts = [row[3] for row in rows[1:] if row[4] != "STATUS"]

    assert len(contexts) == 2
    assert all(original_line in context for context in contexts)
    assert all("PERSON_001" not in context and "EMAIL_001" not in context for context in contexts)


def test_same_line_multiple_detections_create_separate_report_rows(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("Contact Alice Smith at alice@example.com.\n", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    categories = [row[4] for row in rows[1:] if row[4] != "STATUS"]

    assert categories == ["PERSON", "EMAIL"]
