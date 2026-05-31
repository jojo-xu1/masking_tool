# Quickstart: 機密文字列マスキング

## Prerequisites

- Python 3.11
- A local workspace with sample `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf` files
- Default rule files for `en`, `ja`, and `zh`

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run The App

```powershell
python -m masking_tool
```

## Validate Single-File Flow

1. Choose a supported input file.
2. Select one language: English, Japanese, or Chinese.
3. Confirm at least one enabled rule can match the sample file.
4. Start processing.
5. Verify a new `output/YYYYMMDD-HHMMSS/` folder is created.
6. Verify `機密情報検出結果.xlsx` contains required columns.
7. Verify the masked file is under `output/YYYYMMDD-HHMMSS/files/`.
8. Verify the original input file is unchanged.

## Validate Folder Flow

1. Choose a folder containing supported files, unsupported files, and at least one file for each supported language.
2. Start processing without selecting a folder-wide language.
3. Verify supported files are processed or receive clear failure reasons.
4. Verify unsupported files are reported as `skipped_unsupported`.
5. Verify detected languages appear in the report.
6. Verify repeated runs with the same settings produce the same detections and `カテゴリ_連番` values.

## Validate Out-Of-Scope Handling

1. Include a scanned PDF or image-only PDF fixture.
2. Run folder processing.
3. Verify the file is not OCR-processed.
4. Verify the report records it as out of scope or failed with a clear reason.

## Run Tests

```powershell
pytest
```

## Validate Quickstart Files

```powershell
python scripts/validate_quickstart.py
```

Required test coverage:
- Rule schema validation and rule on/off behavior
- Explicit/regex conflict priority
- Deterministic `カテゴリ_連番` assignment
- Text, Office, and text-based PDF replacement fixtures
- Unsupported extension reporting
- Folder-mode language auto-detection
- Excel report columns and risk-level row coloring
- Input non-destruction on success and failure
