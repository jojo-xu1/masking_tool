# Issue: log/csv files are not replaced and other supported files have partial replacement gaps

## Status

Resolved on branch `003-fix-incomplete-replacement-log-csv`.

## Source

- Feature: `002-report-spacy-phone`
- User report: `logファイルとcsvファイルは置換されてない、他のファイルも一部分置換されてない`
- Remote repository: `https://github.com/jojo-xu1/masking_tool.git`

## Problem

Supported file replacement is incomplete:

- `.log` files are detected or included in the supported scope but masked output is not replacing sensitive terms.
- `.csv` files are detected or included in the supported scope but masked output is not replacing sensitive terms.
- Other supported formats may replace only a subset of detected sensitive terms.

This violates the masking contract for supported extensions:

- `.txt`
- `.csv`
- `.log`
- `.docx`
- `.xlsx`
- `.pptx`
- `.pdf`

## Expected Behavior

For every supported input file, all accepted detection matches from explicit rules, regex rules, person-name detection, and phone-number detection are applied to the output copy under `output/YYYYMMDD-HHMMSS/`.

The original input files must remain unchanged.

## Acceptance Criteria

- Processing a folder containing `.log` and `.csv` files produces masked output files where all accepted matches are replaced.
- Processing `.txt`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf` fixtures replaces every accepted match that appears in replaceable text.
- The report rows in `機密情報検出結果.xlsx` align with the actual replacement results in output files.
- Unsupported files continue to be skipped and reported as `skipped_unsupported`.
- OCR, scanned PDFs, image text, and embedded objects remain out of scope.

## Suggested Investigation

- Verify `.log` and `.csv` are routed through the text adapter and output writer, not only file discovery/reporting.
- Add regression coverage for `.log` and `.csv` folder processing with explicit, regex, `PERSON`, and `PHONE` matches.
- Check whether replacement uses accepted conflict-resolution winners consistently across all adapters.
- Check Office/PDF adapters for split text runs, cell boundaries, slide runs, and extracted text spans that may cause partial replacement.

## Related Spec Requirements

- `FR-016`: Person-name and phone-number detections must integrate into the existing `検出語句` -> `置換提案` replacement contract.
- `FR-018`: Supported file scope, output layout, and input non-destruction behavior must remain unchanged.
- `MC-002`: Supported extensions include `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`.
- `MC-006`: Masked files must be written under per-run `output/YYYYMMDD-HHMMSS/` without overwriting input files.

## Proposed Tasks

- [x] Add integration tests for `.log` replacement.
- [x] Add integration tests for `.csv` replacement.
- [x] Add cross-format regression tests that compare report detections with output replacements.
- [x] Keep text-family `.txt`, `.csv`, and `.log` replacement on the block-based processing path.
- [x] Fix adapter-specific partial replacement behavior for Office files where replaceable text was missed.
- [x] Run full regression suite.

## Resolution Notes

- Processing now detects and replaces text per replaceable block instead of flattening an entire document into newline-delimited text and then splitting it back into output structures.
- `.txt`, `.csv`, `.log`, and `.pdf` are treated as single replaceable text blocks.
- `.docx` now includes both body paragraphs and table-cell text in detection and replacement.
- `.xlsx` now replaces each non-empty string cell independently, preserving multiline cell values.
- `.pptx` now includes both normal text-bearing shapes and table-cell text in detection and replacement.
- Japanese folder-language detection now treats kana-free Japanese logs/CSVs with Japanese phone numbers, `.jp` addresses, or Japanese markers as Japanese instead of Chinese.
- Japanese person detection now supplements spaCy with deterministic log/CSV-friendly name patterns for values such as `owner=山田太郎` and CSV name cells such as `佐藤花子`.
- PDF output no longer regenerates a one-page plaintext PDF. It preserves the original PDF pages and applies redaction replacement only to detected terms.
- The same per-run replacement mapper is still shared across blocks, so repeated values continue to reuse the same `カテゴリ_連番`.

## Validation

- `python -m pytest tests/integration/test_supported_format_replacement_coverage.py`
- `python -m pytest tests/integration/test_supported_format_replacement_coverage.py tests/integration/test_folder_language_detection.py tests/unit/test_person_detector.py`
- `python -m pytest tests`
- `python -m compileall src tests scripts`
