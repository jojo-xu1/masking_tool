from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_folder_selection
from masking_tool.core.models import FileStatus
from masking_tool.core.processor import process


def test_folder_processing_continues_after_unsupported(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    (tmp_path / "a.txt").write_text("Alice Smith", encoding="utf-8")
    (tmp_path / "b.bin").write_text("skip", encoding="utf-8")
    _, results = process(make_folder_selection(tmp_path, tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    statuses = {result.target.relative_path.name: result.target.status for result in results}
    assert statuses["a.txt"] == FileStatus.PROCESSED
    assert statuses["b.bin"] == FileStatus.SKIPPED_UNSUPPORTED
