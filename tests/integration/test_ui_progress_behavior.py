from pathlib import Path
from time import monotonic

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_folder_selection
from masking_tool.core.processor import process


def test_duplicate_run_prevention_guard_is_represented_by_running_progress(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "sample.txt").write_text("Contact Alice Smith at alice@example.com", encoding="utf-8")
    seen = []

    process(make_folder_selection(source, tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"), seen.append)

    assert any(progress.is_running for progress in seen)
    assert seen[-1].is_running is False


def test_completion_summary_counts_are_available_from_progress(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "sample.txt").write_text("Contact Alice Smith at alice@example.com", encoding="utf-8")
    (source / "unsupported.md").write_text("Contact Alice Smith", encoding="utf-8")
    seen = []

    process(make_folder_selection(source, tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"), seen.append)

    assert seen[-1].processed_count == 1
    assert seen[-1].skipped_count == 1
    assert seen[-1].failed_count == 0
    assert seen[-1].output_dir is not None


def test_progress_is_visible_within_one_second_of_folder_start(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "sample.txt").write_text("Contact Alice Smith at alice@example.com", encoding="utf-8")
    first_seen = None
    started = monotonic()

    def record(progress) -> None:
        nonlocal first_seen
        if first_seen is None and progress.is_running:
            first_seen = monotonic()

    process(make_folder_selection(source, tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"), record)

    assert first_seen is not None
    assert first_seen - started < 1.0
