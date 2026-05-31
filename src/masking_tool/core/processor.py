from __future__ import annotations

from pathlib import Path
from typing import Callable

from masking_tool.core.discovery import discover_targets
from masking_tool.core.eligibility import apply_eligibility_status
from masking_tool.core.external_permission import permission_snapshot
from masking_tool.core.input_selection import validate_input_selection
from masking_tool.core.models import FileStatus, InputSelection, MaskingRule, ProcessingProgress, SelectionType, TargetFile
from masking_tool.core.output import create_run_output_dir
from masking_tool.core.status import FileProcessingResult
from masking_tool.detection.detector import detect_text
from masking_tool.detection.language import detect_language
from masking_tool.formats.text_adapter import read_text_file, write_text_file
from masking_tool.replacement.apply import apply_replacements
from masking_tool.replacement.mapping import ReplacementMapper
from masking_tool.reporting.excel_report import write_report


def _read_supported_text_blocks(target: TargetFile) -> list[str]:
    if target.extension in {".txt", ".csv", ".log"}:
        return [read_text_file(target.source_path)]
    if target.extension == ".docx":
        from masking_tool.formats.docx_adapter import read_docx_blocks

        return read_docx_blocks(target.source_path)
    if target.extension == ".xlsx":
        from masking_tool.formats.xlsx_adapter import read_xlsx_blocks

        return read_xlsx_blocks(target.source_path)
    if target.extension == ".pptx":
        from masking_tool.formats.pptx_adapter import read_pptx_blocks

        return read_pptx_blocks(target.source_path)
    if target.extension == ".pdf":
        from masking_tool.formats.pdf_adapter import read_pdf_text

        return [read_pdf_text(target.source_path)]
    raise ValueError(f"Unsupported extension: {target.extension}")


def _write_supported_text_blocks(target: TargetFile, output_path: Path, blocks: list[str]) -> None:
    if target.extension in {".txt", ".csv", ".log"}:
        write_text_file(output_path, blocks[0] if blocks else "")
        return
    if target.extension == ".docx":
        from masking_tool.formats.docx_adapter import write_docx_blocks

        write_docx_blocks(target.source_path, output_path, blocks)
        return
    if target.extension == ".xlsx":
        from masking_tool.formats.xlsx_adapter import write_xlsx_blocks

        write_xlsx_blocks(target.source_path, output_path, blocks)
        return
    if target.extension == ".pptx":
        from masking_tool.formats.pptx_adapter import write_pptx_blocks

        write_pptx_blocks(target.source_path, output_path, blocks)
        return
    if target.extension == ".pdf":
        from masking_tool.formats.pdf_adapter import write_pdf_text

        write_pdf_text(target.source_path, output_path, "\n".join(blocks))
        return
    raise ValueError(f"Unsupported extension: {target.extension}")


ProgressCallback = Callable[[ProcessingProgress], None]


def process(
    selection: InputSelection,
    rules: list[MaskingRule],
    progress_callback: ProgressCallback | None = None,
) -> tuple[Path, list[FileProcessingResult]]:
    validate_input_selection(selection)
    permission_snapshot(selection.external_permission)
    output_dir = create_run_output_dir(selection.output_root)
    files_dir = output_dir / "files"
    targets = discover_targets(selection)
    mapper = ReplacementMapper()
    all_detections = []
    results: list[FileProcessingResult] = []

    def emit(current: TargetFile | None = None, running: bool = True) -> None:
        if progress_callback is None:
            return
        progress_callback(
            ProcessingProgress(
                total_targets=len(targets),
                completed_targets=len(results),
                processed_count=sum(1 for result in results if result.status == FileStatus.PROCESSED),
                skipped_count=sum(
                    1
                    for result in results
                    if result.status in {FileStatus.SKIPPED_UNSUPPORTED, FileStatus.SKIPPED_OUT_OF_SCOPE, FileStatus.NO_REPLACEMENT}
                ),
                failed_count=sum(1 for result in results if result.status == FileStatus.FAILED),
                current_target=current.relative_path.as_posix() if current else "",
                output_dir=output_dir,
                is_running=running,
            )
        )

    emit()

    for target in targets:
        emit(target)
        apply_eligibility_status(target)
        if target.status == FileStatus.SKIPPED_UNSUPPORTED:
            results.append(FileProcessingResult(target))
            emit(target)
            continue
        try:
            text_blocks = _read_supported_text_blocks(target)
            text = "\n".join(text_blocks)
            if selection.selection_type == SelectionType.FOLDER:
                language, confidence = detect_language(text)
                if not language:
                    target.status = FileStatus.FAILED
                    target.failure_reason = "Language detection failed"
                    results.append(FileProcessingResult(target))
                    emit(target)
                    continue
                target.applied_language = language
                target.language_confidence = confidence
            detections = []
            masked_blocks: list[str] = []
            next_no = len(all_detections) + 1
            for block in text_blocks:
                block_detections = detect_text(target, block, rules, mapper, next_no)
                detections.extend(block_detections)
                next_no += len(block_detections)
                masked_blocks.append(apply_replacements(block, block_detections) if block_detections else block)
            all_detections.extend(detections)
            output_path = files_dir / target.relative_path
            if detections:
                if target.extension == ".pdf":
                    from masking_tool.formats.pdf_adapter import write_pdf_replacements

                    write_pdf_replacements(target.source_path, output_path, detections)
                else:
                    _write_supported_text_blocks(target, output_path, masked_blocks)
                target.status = FileStatus.PROCESSED
                target.output_path = output_path
            else:
                target.status = FileStatus.NO_REPLACEMENT
            results.append(FileProcessingResult(target, detections))
            emit(target)
        except Exception as exc:
            target.status = FileStatus.FAILED
            target.failure_reason = str(exc)
            results.append(FileProcessingResult(target))
            emit(target)

    write_report(output_dir / "機密情報検出結果.xlsx", all_detections, targets)
    emit(running=False)
    return output_dir, results
