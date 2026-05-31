from pathlib import Path

from masking_tool.core.models import ProcessingProgress


def test_processing_progress_state_fields_and_count_transitions() -> None:
    progress = ProcessingProgress(
        total_targets=3,
        completed_targets=1,
        processed_count=1,
        skipped_count=0,
        failed_count=0,
        current_target="sample.txt",
        output_dir=Path("output/run"),
        is_running=True,
    )

    assert progress.total_targets == 3
    assert progress.completed_targets == 1
    assert progress.current_target == "sample.txt"
    assert progress.is_running
