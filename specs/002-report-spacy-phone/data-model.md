# Data Model: レポート表示改善と人名・電話番号マスク

## Detection Source

Represents where a detection came from.

**Fields**

- `id`: stable source identifier, such as `explicit`, `regex`, `person`, or `phone`
- `category`: report category, including `PERSON` and `PHONE`
- `enabled`: whether the source participates in the current run
- `language`: `en`, `ja`, `zh`, or language-neutral for phone rules
- `required`: whether missing runtime support fails the run
- `order`: deterministic ordering value used after explicit priority and risk

**Validation Rules**

- Japanese and English person detection sources are required when person detection is enabled.
- Chinese person detection uses deterministic fallback detection when the configured spaCy model is unavailable.
- Phone detection is enabled by default and can be disabled.
- Language-separated validation sources must keep English, Japanese, and Chinese samples separate for standard verification.

## Person Name Detection Rule

Configurable detection source for person names.

**Fields**

- `language`: `ja`, `en`, or `zh`
- `model_name`: configured model package/name to load, defaulting to `zh_core_web_sm` for Chinese
- `enabled_by_default`: true
- `unavailable_behavior`: `fail` for `ja` and `en`, `fallback_heuristic` for `zh`
- `risk_level`: expected to be high unless changed by configuration
- `judgment_reason`: report reason text for person-name detections
- `recommended_action`: report action text for person-name detections

**Relationships**

- Produces `Detection Match` records.
- Uses `Replacement Mapping` to create `PERSON_連番`.

## Chinese Person Name Fallback Detection

Deterministic fallback detection used only when the Chinese person detector cannot load the configured spaCy model.

**Fields**

- `language`: `zh`
- `enabled_by_default`: true through the Chinese person detection source
- `unavailable_behavior`: `fallback_heuristic`
- `candidate_context`: Chinese name labels and person-name usage context
- `negative_examples`: phone numbers, dates, project names, and non-person terms

**Validation Rules**

- Fallback matches must produce normal `Detection Match` records with category `PERSON`.
- Repeated Chinese person-name values in the same run must reuse the same `PERSON_連番`.
- The fallback must not block other enabled rules when no Chinese person name is found.

## Phone Number Rule

Default configurable detection source for phone numbers.

**Fields**

- `enabled_by_default`: true
- `supported_regions`: Japan, United States, China
- `supported_forms`: hyphenated, non-hyphenated, country-code-prefixed
- `negative_examples`: dates, postal codes, too-short values, too-long values
- `risk_level`: expected to be high or medium based on configuration
- `judgment_reason`: report reason text for phone detections
- `recommended_action`: report action text for phone detections

**Relationships**

- Produces `Detection Match` records.
- Uses `Replacement Mapping` to create `PHONE_連番`.

## Detection Match

Candidate text span produced by explicit, regex, person, or phone detection.

**Fields**

- `source`: detection source
- `start`: start offset in extracted text
- `end`: end offset in extracted text
- `text`: detected original text
- `category`: report category
- `risk_level`: risk used for conflict resolution and report color
- `rule_order`: deterministic order after explicit priority and risk

**Validation Rules**

- `start` must be less than `end`.
- Accepted matches must not overlap after conflict resolution.
- Conflict priority is explicit first, then higher risk, then existing rule order.

## Replacement Mapping

Per-run deterministic mapping from original values to replacement suggestions.

**Fields**

- `category`: category prefix such as `PERSON` or `PHONE`
- `detected_text`: original detected value
- `replacement`: deterministic label such as `PERSON_001`

**Validation Rules**

- Same `category` and `detected_text` in the same run must produce the same replacement.
- The same detected phone-number value in the same run must produce the same `PHONE_連番`.
- Repeated runs with identical inputs, settings, and languages must produce identical replacements.

## Enhanced Detection Result Row

Report row written to `機密情報検出結果.xlsx`.

**Fields**

- `No`
- `検出語句`
- `置換提案`
- `原文または前後の文脈`
- `情報カテゴリ`
- `リスクレベル`
- `判定理由`
- `推奨対応`

**Validation Rules**

- The workbook must contain exactly these 8 columns in this order.
- Detection rows must include `検出語句`, `置換提案`, category, risk, reason, and action.
- Status-only rows must use the same 8 columns and place target-file clues and status reasons into context, reason, or action fields.

## Report Display Settings

Presentation settings for the generated workbook.

**Fields**

- `freeze_header`: true
- `filters_enabled`: true
- `column_widths`: deterministic widths by required column
- `wrap_columns`: long text columns
- `risk_colors`: high, medium, low, status-only/blank risk

**Validation Rules**

- Header row must be frozen.
- Filters must be enabled for all required columns.
- Risk and status-only coloring must be preserved.

## External Communication Permission

Explicit user permission state required before masking-related content can be transmitted outside the local masking process.

**Fields**

- `permitted`: whether the user explicitly allowed external communication
- `permitted_content`: content classes covered by the permission, such as input content, detected terms, replacement suggestions, or report content
- `target_service`: external service or integration covered by the permission
- `permission_reason`: user-visible reason for the external communication

**Validation Rules**

- Default masking execution must treat `permitted` as false.
- No masking-related content may be transmitted externally unless `permitted` is true for that content and target service.
- Dependency and model installation are outside the masking execution permission state.

## Validation Sample Set

Fixture set used to verify masking behavior without mixing language-specific expectations.

**Fields**

- `language`: `en`, `ja`, or `zh`
- `supported_text_files`: `.txt`, `.csv`, and `.log` samples
- `supported_office_files`: `.docx`, `.xlsx`, and `.pptx` samples
- `supported_pdf_files`: text-based `.pdf` samples
- `unsupported_files`: files expected to be reported as `skipped_unsupported`
- `encoding_notes`: whether UTF-8 BOM or CJK text readability must be checked

**Validation Rules**

- Standard validation samples must not mix English, Japanese, and Chinese content in the same folder.
- Japanese and Chinese samples must contain representative CJK strings that remain readable after extraction.
- Text-family samples with UTF-8 BOM must not include the BOM in detected terms, replacements, or report context.
