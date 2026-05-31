# Test Files

This folder contains sample inputs for manual masking smoke tests.

## Report, spaCy, And Phone Samples

Use `docs/test-files` and `tests/fixtures/text/report_spacy_phone` to verify:

- English and Japanese person names are masked as `PERSON_001`, `PERSON_002`, ...
- Chinese person names are masked with `zh_core_web_sm` when available, or
  deterministic Chinese fallback detection when the model is unavailable.
- Japanese, US, and Chinese phone numbers are masked as `PHONE_001`, `PHONE_002`, ...
- Repeated identical phone numbers in one run reuse the same `PHONE_連番`.
- Dates, postal codes, too-short values, and too-long values remain unmasked.
- UTF-8 BOM in text-family files is not included in detected terms, replacements,
  or report context.
- Japanese and Chinese text remains readable in Office files and text-based PDFs.
- `機密情報検出結果.xlsx` has exactly the required 8 columns, frozen headers,
  filters, wrapped long-text columns, and visible risk/status coloring.
