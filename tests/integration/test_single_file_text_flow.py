from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_single_file_text_flow(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("Contact Alice Smith at alice@example.com.", encoding="utf-8")
    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    masked = output_dir / "files" / "sample.txt"
    assert masked.read_text(encoding="utf-8") == "Contact PERSON_001 at EMAIL_001."
    assert (output_dir / "機密情報検出結果.xlsx").exists()
