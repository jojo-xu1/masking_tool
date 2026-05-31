from pathlib import Path

from masking_tool.core.discovery import discover_targets
from masking_tool.core.input_selection import make_file_selection, make_folder_selection
from masking_tool.core.models import FileStatus
from masking_tool.core.output import create_run_output_dir
from masking_tool.core.eligibility import apply_eligibility_status


def test_output_contract_uses_collision_suffix(tmp_path: Path) -> None:
    first = create_run_output_dir(tmp_path, "20260530-120000")
    second = create_run_output_dir(tmp_path, "20260530-120000")
    assert first.name == "20260530-120000"
    assert second.name == "20260530-120000_001"
    assert (second / "files").is_dir()


def test_unsupported_status_contract(tmp_path: Path) -> None:
    path = tmp_path / "skip.bin"
    path.write_text("x", encoding="utf-8")
    target = discover_targets(make_file_selection(path, "en"))[0]
    apply_eligibility_status(target)
    assert target.status == FileStatus.SKIPPED_UNSUPPORTED
    assert target.failure_reason == "Unsupported extension"
