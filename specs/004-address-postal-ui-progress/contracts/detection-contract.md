# Detection Contract

## Purpose

Address and postal-code detection must enter the same normalized detection, conflict resolution, replacement mapping, file replacement, and report-writing flow as existing explicit, regex, person, and phone detections.

## Inputs

- Extracted replaceable text from a supported file adapter
- Target file metadata, including relative path and applied language
- Enabled detection sources:
  - explicit rules
  - regex rules
  - person-name detection
  - phone-number detection
  - address detection
  - postal-code detection
- Per-run replacement mapper

## Language Preconditions

- Single-file processing must provide a supported language before detection begins.
- If single-file language is missing or unsupported, detection must not run for that file.
- Folder-mode detection sources must run only after a supported language is applied to the target file.
- If folder-mode language detection fails, the target must be marked `failed`, no masked output is written for that target, and the report must include the reason.

## Normalized Match

Each source returns matches with:

```text
source_id
category
risk_level
start
end
text
judgment_reason
recommended_action
order
line_context
```

## Line Context

- `line_context` must be the full original line containing `start` and `end`.
- `line_context` must be captured before any replacement is applied.
- Multiple accepted detections on the same line must each keep the same original line context.

## Address Detection

- Enabled by default.
- Can be disabled by configuration or UI state.
- Accepted address matches use category `ADDRESS`.
- Replacements use `ADDRESS_連番`.
- Japanese files use representative Japan address structures.
- English files use representative US address structures.
- Chinese files use representative China address structures.
- Address detection must require an address label or a clear country-specific structure.
- Ambiguous unlabeled location-like text must not be accepted as an address by default.
- Address matches must exclude adjacent postal-code text when the postal-code segment is separately detected.

## Postal-Code Detection

- Enabled by default.
- Can be disabled by configuration or UI state.
- Accepted postal-code matches use category `POSTAL_CODE`.
- Replacements use `POSTAL_CODE_連番`.
- Japanese files use representative Japan postal-code forms.
- English files use representative US ZIP forms.
- Chinese files use representative China postal-code forms.
- Dates, phone numbers, account numbers, money amounts, and out-of-scope country formats must not be accepted as postal-code matches.

## Adjacent Postal-Code And Address

When a postal code and address are adjacent:

1. the postal-code span must be accepted as `POSTAL_CODE`
2. the address span must be accepted as `ADDRESS`
3. the spans must be non-overlapping
4. output replacement must preserve the order as `POSTAL_CODE_連番` followed by `ADDRESS_連番` when the original order is postal code then address

## Conflict Resolution

When matches overlap, choose the winner by existing behavior:

1. explicit detection first
2. higher risk level
3. existing rule order

Only accepted winners may be used for file replacement or report rows.

## Output

Accepted detections must preserve:

- original detected text in `検出語句`
- deterministic replacement in `置換提案`
- source category in `情報カテゴリ`
- risk level in `リスクレベル`
- source-specific reason and action
- pre-replacement full original line in `原文または前後の文脈`
- span offsets for safe reverse-order replacement

## Validation Fixtures

- English, Japanese, and Chinese fixture sets must include at least one address and postal-code positive case.
- Fixture sets must include one same-line case containing multiple sensitive values.
- Fixture sets must include negative examples for dates, phone numbers, account numbers, money amounts, ambiguous location-like text, and out-of-scope country postal formats.
