# Research: 行単位文脈・住所郵便番号マスク・UI進捗改善

## Line-Based Original Context

**Decision**: Store report context as the full original line containing the detected term before any replacement is applied.

**Rationale**: The report column is used for review and audit. A full pre-replacement line lets reviewers inspect all nearby values, including multiple detections on the same line, without losing the original wording.

**Alternatives considered**:

- Fixed character radius around the match: rejected because it can cut off values on long CSV/log lines and does not guarantee line-level review.
- Replacement-after context: rejected because the specification requires original text before replacement.

## Same-Line Multiple Detections

**Decision**: Treat each accepted match on the same original line as an independent detection row and replacement, while reusing the same line context for each row.

**Rationale**: This preserves the existing one detected term to one replacement suggestion contract and makes category-specific review possible when a line contains person, phone, postal-code, and address values.

**Alternatives considered**:

- Collapse all detections on one line into a single report row: rejected because it would break the `検出語句` -> `置換提案` contract.
- Replace only the first match per line: rejected because it violates the feature requirement and leaves sensitive values unmasked.

## Address Detection Scope

**Decision**: Detect addresses only when they are associated with address labels such as `住所:`, `Address:`, `地址:` or match clear country-specific address structures for the applied language.

**Rationale**: Address detection is prone to false positives. Limiting detection to labels or clear structures keeps v1 predictable and testable while still covering business documents, logs, CSV columns, and Office/PDF samples that identify address fields.

**Alternatives considered**:

- Broad free-form address guessing: rejected because it risks masking non-address location text and increases review burden.
- Postal-code-adjacent addresses only: rejected because labeled address fields may not include postal codes.

## Postal-Code Country Rules

**Decision**: Apply default postal-code rules by applied language and country: Japanese files use representative Japan formats, English files use representative US ZIP formats, and Chinese files use representative China postal-code formats.

**Rationale**: Clarification selected this bounded scope. It provides useful defaults for the existing language sets without introducing global postal-code parsing complexity.

**Alternatives considered**:

- All countries for English files: rejected because scope and false-positive risk are too broad for this feature.
- Country-neutral numeric detection: rejected because dates, phone numbers, account numbers, and money values overlap heavily with postal-like numbers.

## Adjacent Postal-Code And Address Replacement

**Decision**: When postal-code and address text are adjacent, create separate non-overlapping detections and replacements: `POSTAL_CODE_連番` for the postal-code segment and `ADDRESS_連番` for the address segment.

**Rationale**: This keeps postal codes and addresses auditable as distinct categories, maintains deterministic replacement mapping, and avoids losing category information in the report.

**Alternatives considered**:

- Replace the full combined string as `ADDRESS_連番`: rejected because it hides the postal-code category.
- Separate report rows but combined output replacement: rejected because report rows would not match output behavior.

## UI Progress State

**Decision**: Track progress at file level for UI runs, showing running state, processed/skipped/failed counts, duplicate-run prevention, and final output location.

**Rationale**: File-level progress is sufficient for the user-visible requirement, works consistently across supported formats, and avoids overpromising byte-level or page-level progress for Office/PDF adapters.

**Alternatives considered**:

- Indeterminate-only progress: rejected because the user needs visible progress for folder runs.
- Byte-level progress: rejected because adapters do not expose uniform byte-level progress and it would add complexity without improving masking correctness.

## Language Validation And Undetectable Folder Files

**Decision**: Single-file runs with missing or unsupported language selection fail before processing; folder-mode files whose language cannot be determined are marked `failed`, are not written as masked outputs, and are reported with the failure reason.

**Rationale**: The constitution requires explicit single-file language selection and visible handling for folder language detection failure. Failing before processing protects single-file input/output safety, while per-file failure in folder mode allows other files to continue.

**Alternatives considered**:

- Default to English when language is missing or undetectable: rejected because it can apply the wrong country rules and mask incorrectly.
- Treat undetectable files as `skipped_unsupported`: rejected because the extension may be supported; the failure is language applicability, not file support.

## Report And Output Compatibility

**Decision**: Keep the required eight-column report layout and existing per-run output behavior while adding categories `ADDRESS` and `POSTAL_CODE`.

**Rationale**: The constitution requires the existing report and output contract. New categories can be added without changing the workbook column schema or output folder semantics.

**Alternatives considered**:

- Add address/postal audit columns: rejected because report columns must remain exactly the required eight.
- Separate address/postal report sheet: rejected because it would split review across multiple places and is not required.
