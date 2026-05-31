from pathlib import Path

import pytest

from masking_tool.core.input_selection import make_file_selection, validate_input_selection
from masking_tool.core.models import InputSelection, SelectionType
from masking_tool.core.processor import process


def test_single_file_requires_supported_language(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        validate_input_selection(make_file_selection(path, "fr"))


def test_single_file_processing_rejects_missing_language(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    selection = InputSelection(SelectionType.FILE, path, tmp_path / "output")

    with pytest.raises(ValueError, match="Single-file processing requires en, ja, or zh language"):
        process(selection, [])
