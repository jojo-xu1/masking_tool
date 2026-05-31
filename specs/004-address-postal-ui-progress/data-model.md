# Data Model: 行単位文脈・住所郵便番号マスク・UI進捗改善

## Line Context

Full original text line used in `原文または前後の文脈`.

**Fields**

- `target_file`: file that produced the context
- `block_index`: replaceable text block or extracted text block containing the line
- `line_start`: start offset of the line in the block
- `line_end`: end offset of the line in the block
- `line_text`: original line text before replacement

**Validation Rules**

- `line_text` must come from pre-replacement input text.
- A detection row must use the line that contains the accepted detection span.
- Multiple detections on the same line may reuse the same `line_text`.

## Address Detection Rule

Configurable detection source for country-appropriate address values.

**Fields**

- `language`: `ja`, `en`, or `zh`
- `country_scope`: Japan for `ja`, United States for `en`, China for `zh`
- `enabled_by_default`: true unless disabled by user settings
- `category`: `ADDRESS`
- `risk_level`: expected to be high or medium based on configuration
- `address_markers`: labels or country-specific structure markers
- `judgment_reason`: report reason text for address detections
- `recommended_action`: report action text for address detections

**Validation Rules**

- Address detection must be limited to labeled values or clear country-specific structures.
- Ambiguous unlabeled location-like text must not be masked as an address by default.
- Adjacent postal-code text must not be included in the address match when it can be detected separately.

## Postal-Code Detection Rule

Configurable detection source for country-appropriate postal-code values.

**Fields**

- `language`: `ja`, `en`, or `zh`
- `country_scope`: Japan for `ja`, United States for `en`, China for `zh`
- `enabled_by_default`: true unless disabled by user settings
- `category`: `POSTAL_CODE`
- `supported_forms`: country-specific representative forms
- `negative_examples`: dates, phone numbers, account numbers, money amounts, and out-of-scope country formats
- `judgment_reason`: report reason text for postal-code detections
- `recommended_action`: report action text for postal-code detections

**Validation Rules**

- Japanese postal codes use representative Japan patterns.
- English postal codes use representative US ZIP patterns.
- Chinese postal codes use representative China patterns.
- Non-country-scope formats are not masked by default for the applied language.

## Detection Match

Candidate text span produced by explicit, regex, person, phone, address, or postal-code detection.

**Fields**

- `source`: detection source
- `start`: start offset in the replaceable text block
- `end`: end offset in the replaceable text block
- `text`: detected original text
- `category`: report category
- `risk_level`: risk used for conflict resolution and report color
- `rule_order`: deterministic order after explicit priority and risk
- `line_context`: original `Line Context` for reporting

**Validation Rules**

- `start` must be less than `end`.
- Accepted matches must not overlap after conflict resolution.
- Same-line matches must each produce their own detection result.
- Adjacent postal-code and address matches should remain separate, non-overlapping spans.

## Replacement Mapping

Per-run deterministic mapping from original values to replacement suggestions.

**Fields**

- `category`: category prefix such as `ADDRESS` or `POSTAL_CODE`
- `detected_text`: original detected value
- `replacement`: deterministic label such as `ADDRESS_001`

**Validation Rules**

- Same `category` and `detected_text` in the same run must produce the same replacement.
- Repeated runs with identical inputs, settings, and languages must produce identical replacements.
- Postal-code and address values have independent numbering sequences because they are different categories.

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
- `原文または前後の文脈` for detection rows must be the pre-replacement full original line.
- Each accepted detection gets a separate row even when multiple detections share the same line.
- Status-only rows continue to use the same 8-column layout.

## Processing Progress State

Visible UI state for a masking run.

**Fields**

- `total_targets`: number of discovered target files
- `completed_targets`: files with terminal status
- `processed_count`: files processed with replacements
- `skipped_count`: unsupported or out-of-scope files
- `failed_count`: files that failed
- `current_target`: current file clue when available
- `output_dir`: output directory once available
- `is_running`: whether a run is in progress

**Validation Rules**

- UI must prevent starting a second run while `is_running` is true.
- Progress must become visible within 1 second of start for folder runs.
- Completion summary must include processed, skipped, and failed counts.

## Language Application State

Language state used to choose address and postal-code country rules.

**Fields**

- `selection_type`: single file or folder
- `requested_language`: explicit language selected for single-file processing
- `applied_language`: language applied to a target file
- `language_confidence`: confidence or indicator for folder-mode detection when available
- `language_failure_reason`: reason when language is missing, unsupported, or undetectable

**Validation Rules**

- Single-file processing must fail validation before processing if `requested_language` is missing or unsupported.
- Folder-mode targets with no detectable language must be marked `failed`.
- A folder-mode target that fails language detection must not receive a masked output file.
- Language failure reasons must be visible in the report.

## Validation Sample Set

Fixture set used to verify line context, address, postal-code, and UI behavior.

**Fields**

- `language`: `en`, `ja`, or `zh`
- `country_scope`: Japan, United States, or China
- `multi_detection_lines`: lines with multiple expected detections
- `address_examples`: labeled or structurally clear addresses
- `postal_code_examples`: expected country-specific postal codes
- `negative_numeric_examples`: dates, phone numbers, account numbers, money amounts, and out-of-scope postal formats
- `language_failure_examples`: single-file missing/unsupported language cases and folder-mode undetectable text cases
- `ui_folder_sample`: multiple files for progress and summary validation

**Validation Rules**

- Standard validation samples must remain language-separated.
- Expected detections and negative examples must be explicitly marked.
- Samples must include at least one row where postal code and address are adjacent.
- Samples must include a folder-mode language-undetectable case that is reported as failed without output.
