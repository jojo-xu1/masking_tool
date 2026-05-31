from pathlib import Path

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_folder_selection
from masking_tool.core.processor import process


def test_core_processing_progress_callbacks_during_folder_run(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "a.txt").write_text("Contact Alice Smith at alice@example.com", encoding="utf-8")
    (source / "b.md").write_text("unsupported", encoding="utf-8")
    seen = []

    process(make_folder_selection(source, tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"), seen.append)

    assert seen[0].is_running
    assert seen[0].total_targets == 2
    assert seen[-1].is_running is False
    assert seen[-1].completed_targets == 2
    assert seen[-1].processed_count == 1
    assert seen[-1].skipped_count == 1
