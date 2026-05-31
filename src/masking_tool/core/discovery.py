from __future__ import annotations

from pathlib import Path

from masking_tool.core.models import InputSelection, SelectionType, SUPPORTED_EXTENSIONS, TargetFile


def classify_extension(path: Path) -> str:
    return "supported" if path.suffix.lower() in SUPPORTED_EXTENSIONS else "unsupported"


def discover_targets(selection: InputSelection) -> list[TargetFile]:
    if selection.selection_type == SelectionType.FILE:
        path = selection.input_path
        return [
            TargetFile(
                source_path=path,
                relative_path=Path(path.name),
                extension=path.suffix.lower(),
                eligibility=classify_extension(path),
                applied_language=selection.single_file_language,
            )
        ]

    targets: list[TargetFile] = []
    root = selection.input_path
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: str(p.relative_to(root)).lower()):
        targets.append(
            TargetFile(
                source_path=path,
                relative_path=path.relative_to(root),
                extension=path.suffix.lower(),
                eligibility=classify_extension(path),
            )
        )
    return targets
