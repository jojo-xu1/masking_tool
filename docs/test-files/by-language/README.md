# Language-Separated Test Files

Use this folder when you want each input file to contain only one primary
language. The mixed-language stress files remain under `docs/test-files/complex`.

Regenerate these files with:

```powershell
.venv\Scripts\python.exe scripts\generate_language_test_files.py
```

Folder layout:

- `en/`: English-only samples
- `ja/`: Japanese-only samples
- `zh/`: Chinese-only samples

Each language folder contains:

- `.txt`
- `.csv`
- `.log`
- `.docx`
- `.xlsx`
- `.pptx`
- `.pdf`
- `.md` unsupported-file sample

Expected checks:

- Supported files are processed.
- `.md` files are reported as `skipped_unsupported`.
- Email and phone values are masked.
- Address and postal-code values are masked according to each language's first
  version country scope: English/US, Japanese/Japan, and Chinese/China.
- Postal-code values are masked when the context is supplied by inline labels,
  CSV postal-code columns, or XLSX adjacent/header label cells.
- Address and postal-code values on the same line are reported and replaced as
  separate detections.
- Repeated identical phone values reuse the same `PHONE_連番` within one run.
- Repeated identical address and postal-code values reuse the same
  `ADDRESS_連番` and `POSTAL_CODE_連番` within one run.
- Person names are masked when the corresponding person detector is available.
- Dates, postal codes, short numbers, and long account-like numbers are not
  masked as phone numbers.
- Dates, phone numbers, account-like values, ambiguous location notes, and
  out-of-scope country postal formats are not masked by default address or
  postal-code detection.
- Text-family files may include UTF-8 BOM, but BOM must not appear in detected
  terms, replacements, or report context.
- Japanese and Chinese Office files and text-based PDFs must keep CJK text
  readable before and after extraction.
- Manual UI smoke checks should confirm visible folder progress within 1 second,
  duplicate-run prevention, output location display, and processed/skipped/failed
  completion counts.
