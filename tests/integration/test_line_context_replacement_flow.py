from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_same_line_multi_detection_replacement_in_text_file(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.log"
    line = "WARN owner=Alice Smith email=alice@example.com"
    source.write_text(line + "\n", encoding="utf-8")

    output_dir, results = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))

    assert len(results[0].detections) == 2
    assert (output_dir / "files" / "sample.log").read_text(encoding="utf-8") == "WARN owner=PERSON_001 email=EMAIL_001\n"
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    assert [row[3].split(" [file:")[0] for row in rows[1:] if row[4] != "STATUS"] == [line, line]
