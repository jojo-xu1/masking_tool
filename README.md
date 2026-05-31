# Masking Tool

Local desktop tool for masking confidential strings in supported text, Office,
and text-based PDF files.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
python -m spacy download ja_core_news_sm
python -m spacy download zh_core_web_sm
```

If PowerShell blocks activation scripts, use a process-local bypass before
activating:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run

```powershell
python -m masking_tool
```

## Test

```powershell
python -m pytest tests
```

## Scope

Supported extensions are `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`,
and text-based `.pdf`. Image text, scanned PDFs, embedded objects, and OCR are
out of scope for v1.

## Person And Phone Detection

Person-name detection is enabled by default for English and Japanese when the
spaCy language models are installed. If an enabled English or Japanese person
detector cannot load, processing fails with a visible reason. Chinese person
detection uses `zh_core_web_sm` when available and falls back to deterministic
Chinese name-pattern detection when that model is unavailable.

Phone detection is enabled by default for representative Japanese, US, and
Chinese phone-number formats. Person and phone detection sources can be disabled
through their rule/source configuration when only explicit and regex masking is
desired.

## Address, Postal Code, And UI Progress

Address and postal-code detection is enabled by default for English, Japanese,
and Chinese. The first version intentionally uses representative country scopes:
Japanese files use Japan formats, English files use US formats, and Chinese files
use China formats. Addresses are detected only when an address label is present
or the text has a clear country-specific address structure. Ambiguous location
notes and out-of-scope country formats are left unchanged by default.

The desktop UI includes toggles for person, phone, address, and postal-code
detection. Folder runs show progress, block duplicate starts while processing is
running, and show the output location plus processed, skipped, and failed counts
after completion.

## External Communication

Masking runs are local by default. Input content, detected terms, replacement
suggestions, and report content must not be transmitted to an external service
unless the user explicitly permits that communication for the target service and
content type. Installing dependencies or spaCy model packages can still use the
normal package sources before a masking run starts.
