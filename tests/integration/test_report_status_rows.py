from pathlib import Path

import pytest

from masking_tool.core.models import FileStatus, TargetFile
from masking_tool.reporting.excel_report import write_report


def _target(name: str, status: FileStatus, reason: str | None = None) -> TargetFile:
    return TargetFile(
        source_path=Path(name),
        relative_path=Path(name),
        extension=Path(name).suffix,
        eligibility="eligible",
        applied_language="en",
        status=status,
        failure_reason=reason,
    )


def test_status_rows_use_required_columns(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "機密情報検出結果.xlsx"
    targets = [
        _target("unsupported.md", FileStatus.SKIPPED_UNSUPPORTED, "Unsupported extension"),
        _target("empty.txt", FileStatus.NO_REPLACEMENT),
        _target("failed.txt", FileStatus.FAILED, "Read failed"),
    ]

    write_report(path, [], targets)
    sheet = openpyxl.load_workbook(path)["検出結果"]
    rows = list(sheet.iter_rows(values_only=True))

    assert sheet.max_column == 8
    assert len(rows) == 4
    assert rows[1][4] == "STATUS"
    assert "unsupported.md" in rows[1][3]
    assert rows[3][6] == "Read failed"
