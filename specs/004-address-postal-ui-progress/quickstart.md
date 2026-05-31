# Quickstart: 行単位文脈・住所郵便番号マスク・UI進捗改善

## Prerequisites

- Python 3.11 or later
- Project dependencies installed
- Existing person-name detection model requirements satisfied when person detection is enabled

PowerShell script activation may be blocked by local policy. In that case, run commands through the virtual environment Python directly or use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run Unit And Contract Tests

```powershell
python -m pytest tests\unit tests\contract
```

If the Windows user-profile temp directory is not writable, run pytest with
repository-local temp and cache directories:

```powershell
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp -o cache_dir=.pytest-cache-local tests
```

Expected coverage:

- address detection for representative Japan, US, and China structures
- postal-code detection for representative Japan, US, and China formats
- postal-code false-positive examples
- single-file missing or unsupported language validation
- folder-mode language-undetectable failure behavior
- adjacent postal-code and address are reported and replaced separately
- same-line multiple detections each produce a report row
- report context uses the pre-replacement original line
- detection-source on/off behavior for address and postal-code rules

## Run Integration Tests

```powershell
python -m pytest tests\integration
```

Expected coverage:

- single-file language selection
- folder-mode language handling
- supported file processing for `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf`
- unsupported file skip reporting
- input file non-destruction
- reproducible `ADDRESS_連番` and `POSTAL_CODE_連番`
- language-separated English/US, Japanese/Japan, and Chinese/China validation samples
- UI progress state and completion summary behavior
- folder-mode language-undetectable files reported as failed without masked output

## Manual Smoke Test

1. Use language-separated sample folders under `docs/test-files/by-language/`.
2. Add or choose samples containing:
   - one line with person, phone, postal code, and address
   - Japanese address and postal code
   - US address and ZIP code
   - Chinese address and postal code
   - ambiguous location-like text marked as a negative example
   - out-of-scope postal formats for the applied language
3. Run masking from the UI using folder mode.
4. Confirm the progress bar appears within 1 second and advances by file completion.
5. Confirm the run button cannot start a duplicate run while processing.
6. Open the generated per-run `output/YYYYMMDD-HHMMSS/機密情報検出結果.xlsx`.
7. Confirm:
   - workbook has exactly 8 columns
   - all expected same-line values are reported as separate rows
   - `原文または前後の文脈` shows the pre-replacement original line
   - addresses are masked as `ADDRESS_連番`
   - postal codes are masked as `POSTAL_CODE_連番`
   - adjacent postal code and address are replaced separately
   - negative numeric and ambiguous address examples are not masked
   - original input files are unchanged

## Required Failure Check

1. Run a single-file input without a supported language selection. Processing must fail before masking and leave input/output files unchanged.
2. Run a folder containing one language-undetectable supported file, one unsupported file, and one file with no replacements. The run must continue for other files, avoid writing masked output for the language-undetectable file, and distinguish processed, skipped, failed, and no-replacement outcomes without adding report columns.
