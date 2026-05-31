from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_single_file_input_is_not_modified(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    original = "Contact Alice Smith at alice@example.com."
    source.write_text(original, encoding="utf-8")
    process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    assert source.read_text(encoding="utf-8") == original
