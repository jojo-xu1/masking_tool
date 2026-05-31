# Research: レポート表示改善と人名・電話番号マスク

## spaCy Model Loading

**Decision**: Add spaCy as the primary person-name detection engine and load language-specific trained pipeline packages by model name. English and Japanese model availability is required when person-name detection is enabled; Chinese person-name detection uses the configured spaCy model when available and deterministic Chinese fallback detection when the model is unavailable.

**Rationale**: spaCy official documentation treats trained pipelines as installable Python packages and recommends loading them by package/model name. The feature requires spaCy adoption, Japanese and English are mandatory from clarification, and the later Chinese-support refinement requires masking representative Chinese person names even when the optional Chinese model package is not installed.

**Alternatives considered**:

- Regex-only person detection: rejected because the feature explicitly asks for spaCy and regex-only would miss many names.
- Always skip unavailable models: rejected for Japanese/English because clarification requires visible failure when mandatory detection cannot run, and rejected for Chinese because representative Chinese person names must still be masked.
- Require Chinese model installation: rejected because the tool should support Chinese samples without making the optional Chinese model a blocking dependency.

## Person Detection Pipeline Integration

**Decision**: Represent person detections as normal detection matches with category `PERSON`, high risk, deterministic rule order, and `PERSON_連番` replacement generation through the existing mapper.

**Rationale**: The constitution requires all masking to flow through the `検出語句` -> `置換提案` contract. Reusing the existing match/conflict/replacement path keeps report rows, replacements, and reproducibility consistent with explicit and regex rules.

**Alternatives considered**:

- Apply person replacements outside the rule pipeline: rejected because it would create a second replacement contract.
- Store original names in a separate report sheet: rejected because the clarified report layout must keep exactly 8 columns.

## Phone Number Detection

**Decision**: Add configurable default phone-number detection for representative Japanese, US, and Chinese formats, including hyphenated, non-hyphenated, and country-code-prefixed values.

**Rationale**: Clarification selected Japan/US/China representative formats. A configurable default rule fits the existing settings model and allows users to disable it when false positives are unacceptable.

**Alternatives considered**:

- Fully global phone parsing: rejected as broader than required and likely to increase false positives.
- Japan-only phone detection: rejected because clarification selected Japan/US/China.

## Phone Number Replacement Reuse

**Decision**: Reuse the same `PHONE_連番` replacement suggestion for the same detected phone-number value within a processing run.

**Rationale**: This matches the existing deterministic replacement contract and the clarified behavior for repeated phone numbers. It also keeps report review and repeated-run comparisons straightforward.

**Alternatives considered**:

- Generate a new replacement for each occurrence: rejected because it weakens reproducibility and makes report review noisier.
- Scope reuse by file only: rejected because the replacement mapper already operates at run scope for identical detected values.

## Numeric False-Positive Controls

**Decision**: Treat dates, postal codes, and too-short/too-long numeric strings as explicit negative fixtures and block them from `PHONE` matches.

**Rationale**: The specification requires 0 fixture values marked as non-phone examples to be masked as phone numbers. Contract tests can capture this behavior without overfitting every international numbering rule.

**Alternatives considered**:

- Length-only filtering: rejected because dates and postal codes can have similar lengths.
- Context-only filtering: rejected because context may be absent in tabular and log files.

## Excel Report Layout

**Decision**: Keep exactly the required 8 report columns. Put target-file clues, skipped/failed status, and reasons into `原文または前後の文脈`, `判定理由`, and `推奨対応` instead of adding audit columns.

**Rationale**: Clarification selected the 8-column layout, and the constitution requires those columns. Readability improvements should use freeze panes, filters, column widths, wrapping, and row colors without adding columns.

**Alternatives considered**:

- Additional audit columns: rejected by clarification.
- Separate status sheet: rejected by clarification.

## Language-Separated Validation And CJK Encoding

**Decision**: Keep standard validation samples separated by primary language and include UTF-8 text, Office, and text-based PDF samples whose Japanese and Chinese characters are readable before and after extraction.

**Rationale**: Language-separated samples avoid ambiguity in language-specific detection behavior, while explicit CJK and UTF-8 BOM coverage prevents Windows-created test files from hiding encoding regressions.

**Alternatives considered**:

- Use only mixed-language stress files: rejected because failures are harder to attribute to a language-specific rule or model.
- Validate text files only: rejected because the supported scope includes Office files and text-based PDFs.

## Conflict Resolution

**Decision**: Resolve overlapping explicit, regex, person, and phone detections by explicit match first, then higher risk, then existing rule order.

**Rationale**: Clarification selected this order. It preserves user-intended explicit replacements while keeping high-risk detections ahead of lower-risk detections.

**Alternatives considered**:

- Longest match wins: rejected because it could override explicit user-specified masking.
- Person/phone always wins: rejected because it would weaken user-provided rules.

## External Communication Permission

**Decision**: Keep masking execution local by default and require an explicit user permission state before transmitting input content, detected terms, replacement suggestions, or report content to any external service.

**Rationale**: The tool processes confidential content, so default local execution minimizes disclosure risk. Allowing external communication only after explicit permission preserves future integration flexibility while keeping the current masking path safe and auditable.

**Alternatives considered**:

- Always prohibit external communication: rejected because clarification allows external communication when the user explicitly permits it.
- Allow external services by default: rejected because it creates unnecessary privacy risk for confidential masking inputs.

## Sources

- spaCy Models & Languages documentation: https://spacy.io/usage/models/
- spaCy installation documentation: https://spacy.io/usage
