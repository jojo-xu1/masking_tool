from pathlib import Path

from masking_tool.core.discovery import discover_targets
from masking_tool.core.eligibility import apply_eligibility_status
from masking_tool.core.input_selection import make_folder_selection
from masking_tool.core.models import FileStatus


def test_unsupported_files_are_marked(tmp_path: Path) -> None:
    (tmp_path / "a.bin").write_text("x", encoding="utf-8")
    target = discover_targets(make_folder_selection(tmp_path))[0]
    apply_eligibility_status(target)
    assert target.status == FileStatus.SKIPPED_UNSUPPORTED
