# Detection Contract

## Purpose

All detection sources must produce normalized matches that can enter the existing conflict resolution, replacement mapping, file replacement, and report-writing flow.

## Inputs

- Extracted plain text from a supported file adapter
- Target file metadata, including relative path and applied language
- Enabled detection sources:
  - explicit rules
  - regex rules
  - person-name detection
  - phone-number detection
- Per-run replacement mapper

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
```

## Person Detection

- Enabled by default.
- Can be disabled by configuration or UI state.
- Japanese and English support is required when enabled.
- If required Japanese or English person detection cannot run, processing fails with a visible reason.
- Chinese support uses the configured spaCy model when available; when unavailable, deterministic Chinese fallback detection is used instead of skipping representative Chinese person names.
- Accepted person matches use category `PERSON`.
- Replacements use `PERSON_連番`.
- Repeated Chinese person-name values in one processing run must reuse the same `PERSON_連番`.

## Phone Detection

- Enabled by default.
- Can be disabled by configuration or UI state.
- Supports representative Japanese, US, and Chinese phone-number forms.
- Supports hyphenated, non-hyphenated, and country-code-prefixed forms.
- Must not accept fixture examples marked as dates, postal codes, too short, or too long.
- Accepted phone matches use category `PHONE`.
- Replacements use `PHONE_連番`.
- The same detected phone-number value in one processing run must reuse the same `PHONE_連番`.

## Conflict Resolution

When matches overlap, choose the winner by:

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
- span offsets for safe reverse-order replacement

## External Communication Guard

- Detection and replacement must run locally by default.
- Input content, detected terms, replacement suggestions, and report content must not be transmitted to an external service unless an explicit user permission state allows that content and service.
- Missing external permission must not block local regex, explicit, person-name, phone-number, report, or file-output behavior.

## Validation Fixtures

- Standard validation fixtures must be grouped by primary language: English, Japanese, and Chinese.
- Text-family fixtures may include UTF-8 BOM and must not expose the BOM in matches or report context.
- Office and text-based PDF fixtures containing Japanese or Chinese text must remain readable after extraction.
