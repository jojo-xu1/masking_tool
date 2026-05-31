from __future__ import annotations

from pathlib import Path

from masking_tool.core.models import InputSelection, SelectionType, SUPPORTED_LANGUAGES


def validate_input_selection(selection: InputSelection) -> None:
    path = selection.input_path
    if selection.selection_type == SelectionType.FILE:
        if not path.is_file():
            raise ValueError(f"Input file does not exist: {path}")
        if selection.single_file_language not in SUPPORTED_LANGUAGES:
            raise ValueError("Single-file processing requires en, ja, or zh language")
    elif selection.selection_type == SelectionType.FOLDER:
        if not path.is_dir():
            raise ValueError(f"Input folder does not exist: {path}")
    else:
        raise ValueError(f"Unsupported selection type: {selection.selection_type}")


def make_file_selection(path: str | Path, language: str, output_root: str | Path = "output") -> InputSelection:
    return InputSelection(SelectionType.FILE, Path(path), Path(output_root), language)


def make_folder_selection(path: str | Path, output_root: str | Path = "output") -> InputSelection:
    return InputSelection(SelectionType.FOLDER, Path(path), Path(output_root), None, "auto_detect")
