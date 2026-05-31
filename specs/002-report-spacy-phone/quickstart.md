# Quickstart: レポート表示改善と人名・電話番号マスク

## Prerequisites

- Python 3.11 or later
- Project dependencies installed
- spaCy English and Japanese model packages installed for enabled person-name detection
- Optional spaCy Chinese model package `zh_core_web_sm` installed for model-based Chinese person-name detection

PowerShell script activation may be blocked by local policy. In that case, run commands through the virtual environment Python directly or use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Install

```powershell
python -m pip install -e .[dev]
python -m spacy download en_core_web_sm
python -m spacy download ja_core_news_sm
python -m spacy download zh_core_web_sm
```

Chinese person-name detection uses `zh_core_web_sm` when available and falls back to deterministic Chinese person-name detection when the model is unavailable.

## Run Unit And Contract Tests

```powershell
python -m pytest tests\unit tests\contract
```

Expected coverage:

- person detection source availability behavior
- phone matching and false-positive examples
- repeated phone-number values reuse the same `PHONE_連番`
- conflict resolution order
- 8-column report contract and formatting
- UTF-8 BOM handling without leaking BOM into matches or report context
- default masking execution does not require external communication

## Run Integration Tests

```powershell
python -m pytest tests\integration
```

Expected coverage:

- single-file language selection
- folder-mode language detection
- supported file processing
- unsupported file skip reporting
- input file non-destruction
- reproducible `PERSON_連番` and `PHONE_連番`
- language-separated English, Japanese, and Chinese validation samples
- readable Japanese and Chinese text in Office and text-based PDF samples
- external communication paths require explicit user permission before transmitting masking-related content

## Manual Smoke Test

1. Use language-separated sample folders under `docs/test-files/by-language/`.
2. In each target language folder, use samples containing language-appropriate values:
   - English folder: English person name and US phone number
   - Japanese folder: Japanese person name and Japanese phone number
   - Chinese folder: Chinese text and Chinese phone number
   - repeated phone-number value
   - date and postal-code negative examples
3. Run masking from the UI or CLI using the existing workflow.
4. Open the generated per-run `output/YYYYMMDD-HHMMSS/機密情報検出結果.xlsx`.
5. Confirm:
   - workbook has exactly 8 columns
   - header row is frozen
   - filters are enabled
   - long text columns wrap
   - risk/status coloring is visible
   - person names, including representative Chinese person names, are masked as `PERSON_連番`
   - phone numbers are masked as `PHONE_連番`
   - repeated phone numbers reuse the same `PHONE_連番` within the run
   - negative numeric examples are not masked as phone numbers
   - Japanese and Chinese text remains readable in extracted text and report context
   - no external communication is required unless explicitly permitted
   - original input files are unchanged

## Required Failure Check

With person-name detection enabled, temporarily remove or misconfigure the English or Japanese person detection model and run a matching-language file. Processing must fail with a visible reason instead of silently continuing.
