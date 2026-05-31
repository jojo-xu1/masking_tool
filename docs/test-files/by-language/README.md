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
- Repeated identical phone values reuse the same `PHONE_連番` within one run.
- Person names are masked when the corresponding person detector is available.
- Dates, postal codes, short numbers, and long account-like numbers are not
  masked as phone numbers.
- Text-family files may include UTF-8 BOM, but BOM must not appear in detected
  terms, replacements, or report context.
- Japanese and Chinese Office files and text-based PDFs must keep CJK text
  readable before and after extraction.
