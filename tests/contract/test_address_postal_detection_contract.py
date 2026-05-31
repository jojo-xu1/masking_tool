from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_files
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_address_and_postal_detections_use_required_categories_and_replacements(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("Postal code: 10001\nAddress: 123 Market Street, New York, NY\n", encoding="utf-8")

    output_dir, _ = process(
        make_file_selection(source, "en", tmp_path / "output"),
        load_rule_files(["src/masking_tool_defaults/en.yml"]),
    )
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    by_category = {row[4]: row for row in rows[1:] if row[4] != "STATUS"}

    assert by_category["POSTAL_CODE"][2] == "POSTAL_CODE_001"
    assert by_category["ADDRESS"][2] == "ADDRESS_001"
    assert by_category["POSTAL_CODE"][6]
    assert by_category["ADDRESS"][7]
