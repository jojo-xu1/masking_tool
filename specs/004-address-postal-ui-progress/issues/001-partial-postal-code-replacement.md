# Issue: Some postal-code values are not replaced

## Status

Open.

## Source

- Feature: `004-address-postal-ui-progress`
- User report: `一部分の郵便番号が置換されてない`
- Remote repository: `https://github.com/jojo-xu1/masking_tool.git`

## Problem

Postal-code masking is incomplete. Some postal-code values that should be
accepted for the applied language and country scope are left unchanged in masked
output files.

Likely high-risk areas:

- Text-family files where postal codes appear as field values, such as
  `postal=10001`, `zip=10001`, `郵便番号=100-0001`, or `邮编=100000`.
- CSV cells where the column name identifies the value as a postal code but the
  cell itself has no inline label.
- Same-line multi-detection rows where postal code, address, person, and phone
  appear together.
- Office/PDF extracted text blocks where labels and values may be split or
  normalized differently from plain text fixtures.

This violates the feature contract that accepted postal-code detections are
reported with category `POSTAL_CODE` and replaced as `POSTAL_CODE_連番`.

## Expected Behavior

For English/US, Japanese/Japan, and Chinese/China inputs, every postal-code
value that is supported by the default country-specific rule scope and is
identified by a label, field name, clear address context, or configured source
must be replaced in the output file.

False positives must still be avoided for dates, phone numbers, account numbers,
money values, and out-of-scope country formats.

## Acceptance Criteria

- English ZIP values are replaced when written as `ZIP: 10001`,
  `Postal code: 10001`, `postal=10001`, or in a CSV `postal`/`zip` column.
- Japanese postal codes are replaced when written as `〒100-0001`,
  `郵便番号: 100-0001`, `postal=100-0001`, or in a CSV `postal`/`郵便番号` column.
- Chinese postal codes are replaced when written as `邮政编码: 100000`,
  `邮编=100000`, or in a CSV `postal`/`邮政编码` column.
- Postal-code replacement works consistently across `.txt`, `.csv`, `.log`,
  `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf` where the value is in
  replaceable text.
- Same-line postal-code values are replaced even when person, phone, address, or
  email values are also detected on that line.
- Dates, phone numbers, account-like values, money values, and out-of-scope
  country formats remain unmasked by default postal-code detection.
- `機密情報検出結果.xlsx` contains one row per accepted postal-code detection
  with the original pre-replacement line context.

## Suggested Investigation

- Inspect `src/masking_tool/detection/postal.py` for label handling that only
  recognizes colon-style labels and misses equals-style key/value text.
- Add CSV-aware context tests where postal-code values are inferred from column
  headers.
- Verify that postal detection runs before overlap resolution and that phone
  detection does not incorrectly win postal-code spans.
- Check generated fixtures in `scripts/generate_language_test_files.py` and
  `docs/test-files/by-language/` for postal examples that are expected to mask
  but currently remain unchanged.
- Confirm Office/PDF adapters preserve enough label/value context for postal
  detection, or add block-level tests for extracted text forms.

## Related Spec Requirements

- `FR-005`: System MUST support configurable postal-code detection as a default
  detection category for English, Japanese, and Chinese files.
- `FR-006`: System MUST apply country-appropriate address and postal-code rules
  based on the file's applied language.
- `FR-008`: System MUST mask detected postal codes using deterministic
  `POSTAL_CODE_連番` replacement suggestions.
- `FR-011`: System MUST report postal-code detections with information category
  `POSTAL_CODE`, risk level, judgment reason, and recommended action.
- `FR-012`: System MUST avoid classifying dates, phone numbers, account numbers,
  money amounts, and other clearly non-postal numeric values as postal codes.
- `FR-021`: System MUST treat adjacent postal-code and address text as separate
  detections and separate replacements.

## Proposed Tasks

- [ ] Add unit tests for equals-style postal labels in
  `tests/unit/test_postal_detector.py`.
- [ ] Add CSV header-aware postal-code detection coverage for English, Japanese,
  and Chinese in `tests/integration/test_address_postal_masking_flow.py`.
- [ ] Add log key/value postal-code coverage for English, Japanese, and Chinese
  in `tests/integration/test_address_postal_masking_flow.py`.
- [ ] Add cross-format regression coverage to confirm postal-code values are
  replaced in text, Office, and text-based PDF adapters.
- [ ] Update `src/masking_tool/detection/postal.py` to accept supported
  label/value variants while preserving false-positive filters.
- [ ] Refresh language-separated fixtures and documentation expectations if the
  accepted postal label forms are expanded.
- [ ] Run focused postal validation and full regression:
  `python -m pytest tests/unit/test_postal_detector.py tests/integration/test_address_postal_masking_flow.py tests`

## GitHub Sync

GitHub issue creation was not executed from this environment because no GitHub
MCP tool or `gh` CLI is available. This file is the issue body to sync to
`jojo-xu1/masking_tool` when GitHub issue creation is available.
