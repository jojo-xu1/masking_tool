from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_repeated_runs_have_same_masked_content(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("Alice Smith alice@example.com", encoding="utf-8")
    rules = load_rule_file("tests/fixtures/rules/test_rules.yml")
    out1, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)
    out2, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)
    assert (out1 / "files" / "sample.txt").read_text(encoding="utf-8") == (out2 / "files" / "sample.txt").read_text(encoding="utf-8")
