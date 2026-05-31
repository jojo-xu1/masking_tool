from pathlib import Path

from masking_tool.core.discovery import discover_targets
from masking_tool.core.input_selection import make_folder_selection


def test_folder_discovery_is_recursive(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "a.txt").write_text("x", encoding="utf-8")
    targets = discover_targets(make_folder_selection(tmp_path))
    assert [str(target.relative_path).replace("\\", "/") for target in targets] == ["nested/a.txt"]
