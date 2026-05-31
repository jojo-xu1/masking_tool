# Tasks: レポート表示改善と人名・電話番号マスク

**Input**: Design documents from `/specs/002-report-spacy-phone/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by constitution gates for masking replacement, report integrity, configuration on/off behavior, reproducibility, unsupported skips, folder processing, language behavior, and input non-destruction.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- All task descriptions include exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies, fixtures, and test entry points shared by all stories.

- [X] T001 Add spaCy runtime dependency and documented English/Japanese model setup in pyproject.toml and README.md
- [X] T002 [P] Add representative English, Japanese, and Chinese person/phone fixture text files in tests/fixtures/text/report_spacy_phone/
- [X] T003 [P] Add numeric negative fixture data for dates, postal codes, too-short values, and too-long values in tests/fixtures/text/report_spacy_phone/
- [X] T004 [P] Add quickstart validation notes for this feature to docs/test-files/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared detection contracts and configuration support that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 Extend RuleType or add a detection source abstraction for regex, explicit, person, and phone sources in src/masking_tool/core/models.py
- [X] T006 Create normalized detection match helpers shared by explicit, regex, person, and phone detections in src/masking_tool/detection/matches.py
- [X] T007 Update existing regex/explicit rule matching to return normalized matches in src/masking_tool/detection/rules.py
- [X] T008 Update conflict resolution priority to explicit first, higher risk second, existing rule order third in src/masking_tool/detection/rules.py
- [X] T009 Add detection source on/off state support for person and phone sources in src/masking_tool/config/rule_state.py
- [X] T010 Update rule configuration loading to accept source-level defaults and preserve existing YAML compatibility in src/masking_tool/config/loader.py
- [X] T011 Update default English, Japanese, and Chinese rule files with configurable person and phone source metadata in src/masking_tool_defaults/en.yml, src/masking_tool_defaults/ja.yml, and src/masking_tool_defaults/zh.yml
- [X] T012 Add unit tests for normalized match shape and conflict priority in tests/unit/test_detection_matches.py

**Checkpoint**: Foundation ready. User story work can start independently.

---

## Phase 3: User Story 1 - 検出結果 Excel を読みやすく確認する (Priority: P1) MVP

**Goal**: Generate `機密情報検出結果.xlsx` with exactly 8 required columns, frozen header, filters, readable widths, wrapping, risk/status colors, and status information folded into existing columns.

**Independent Test**: Generate a report with detection rows plus skipped/failed/no-replacement rows and verify the workbook opens with the required 8 columns and formatting.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract test for exactly 8 report columns and no audit columns in tests/contract/test_report_contract.py
- [X] T014 [P] [US1] Add contract test for frozen header, filters, widths, wrapping, and risk/status row fills in tests/contract/test_report_display_formatting.py
- [X] T015 [P] [US1] Add integration test for unsupported, no-replacement, and failed status-only rows using required columns in tests/integration/test_report_status_rows.py

### Implementation for User Story 1

- [X] T016 [US1] Remove appended audit columns and keep REQUIRED_COLUMNS as the only workbook columns in src/masking_tool/reporting/excel_report.py
- [X] T017 [US1] Rework detection_row and status_row to place target-file clues, status, and reasons into context, judgment reason, and recommended action fields in src/masking_tool/reporting/excel_report.py
- [X] T018 [US1] Apply freeze panes, autofilter, deterministic column widths, text wrapping, and header styling in src/masking_tool/reporting/excel_report.py
- [X] T019 [US1] Preserve risk-level coloring and add visually distinct status-only row coloring in src/masking_tool/reporting/excel_report.py
- [X] T020 [US1] Update single-file report integration expectations for the 8-column layout in tests/integration/test_single_file_report.py
- [X] T021 [US1] Run focused report tests with python -m pytest tests/contract/test_report_contract.py tests/contract/test_report_display_formatting.py tests/integration/test_report_status_rows.py tests/integration/test_single_file_report.py

**Checkpoint**: User Story 1 is independently functional and is the MVP.

---

## Phase 4: User Story 2 - 人名を自動検出してマスクする (Priority: P2)

**Goal**: Detect Japanese and English person names with spaCy when enabled, mask them as deterministic `PERSON_連番`, and fail visibly if required Japanese/English detection support is unavailable.

**Independent Test**: Process Japanese and English samples containing person names and confirm `PERSON_連番` replacements, report category `PERSON`, deterministic reuse, disable behavior, and required-model failure behavior.

### Tests for User Story 2

- [X] T022 [P] [US2] Add unit tests for spaCy model loading, unavailable Japanese/English failure, and Chinese fallback behavior in tests/unit/test_person_detector.py
- [X] T023 [P] [US2] Add unit tests for PERSON match normalization and deterministic replacement mapping in tests/unit/test_person_detection_matches.py
- [X] T024 [P] [US2] Add contract tests for person detection contract behavior in tests/contract/test_detection_contract.py
- [X] T025 [P] [US2] Add integration test for Japanese and English person masking flow in tests/integration/test_person_masking_flow.py
- [X] T026 [P] [US2] Add integration test for disabling person detection while preserving regex and explicit rules in tests/integration/test_person_toggle_behavior.py

### Implementation for User Story 2

- [X] T027 [US2] Implement spaCy-backed person detector with model cache and language-specific unavailable behavior in src/masking_tool/detection/person.py
- [X] T028 [US2] Integrate person-name matches into detect_text before conflict resolution in src/masking_tool/detection/detector.py
- [X] T029 [US2] Add PERSON rule metadata and default enabled state to English and Japanese defaults in src/masking_tool_defaults/en.yml and src/masking_tool_defaults/ja.yml
- [X] T030 [US2] Add Chinese PERSON metadata with fallback unavailable behavior in src/masking_tool_defaults/zh.yml
- [X] T031 [US2] Surface person-detection enabled/disabled state in UI settings or processing state in src/masking_tool/ui/settings_panel.py and src/masking_tool/ui/main_window.py
- [X] T032 [US2] Ensure required person detector failures set visible failure reasons without overwriting inputs in src/masking_tool/core/processor.py
- [X] T033 [US2] Run focused person tests with python -m pytest tests/unit/test_person_detector.py tests/unit/test_person_detection_matches.py tests/contract/test_detection_contract.py tests/integration/test_person_masking_flow.py tests/integration/test_person_toggle_behavior.py

**Checkpoint**: User Story 2 works independently with existing report and replacement contracts.

---

## Phase 5: User Story 3 - 電話番号をマスクする (Priority: P3)

**Goal**: Detect representative Japanese, US, and Chinese phone numbers, mask them as deterministic `PHONE_連番`, and avoid date/postal/invalid numeric false positives.

**Independent Test**: Process samples containing phone numbers and negative numeric examples, then confirm expected phone values are masked and negative fixtures remain unchanged.

### Tests for User Story 3

- [X] T034 [P] [US3] Add unit tests for Japanese, US, and Chinese phone formats in tests/unit/test_phone_detector.py
- [X] T035 [P] [US3] Add unit tests for phone false-positive exclusions in tests/unit/test_phone_false_positives.py
- [X] T036 [P] [US3] Add contract tests for PHONE detection category and replacement contract in tests/contract/test_phone_detection_contract.py
- [X] T037 [P] [US3] Add integration test for phone masking and deterministic reruns in tests/integration/test_phone_masking_flow.py
- [X] T038 [P] [US3] Add integration test for disabling phone detection while preserving other rules in tests/integration/test_phone_toggle_behavior.py

### Implementation for User Story 3

- [X] T039 [US3] Implement representative Japan, US, and China phone detection with negative filters in src/masking_tool/detection/phone.py
- [X] T040 [US3] Integrate phone matches into detect_text before conflict resolution in src/masking_tool/detection/detector.py
- [X] T041 [US3] Add PHONE metadata and default enabled state to src/masking_tool_defaults/en.yml, src/masking_tool_defaults/ja.yml, and src/masking_tool_defaults/zh.yml
- [X] T042 [US3] Surface phone-detection enabled/disabled state in UI settings or processing state in src/masking_tool/ui/settings_panel.py and src/masking_tool/ui/main_window.py
- [X] T043 [US3] Run focused phone tests with python -m pytest tests/unit/test_phone_detector.py tests/unit/test_phone_false_positives.py tests/contract/test_phone_detection_contract.py tests/integration/test_phone_masking_flow.py tests/integration/test_phone_toggle_behavior.py

**Checkpoint**: User Story 3 works independently with existing report and replacement contracts.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Validate constitution gates, documentation, and full-system behavior after selected stories are complete.

- [X] T044 [P] Update README.md with spaCy model setup, PowerShell activation workaround, and person/phone toggle behavior
- [X] T045 [P] Update docs/test-files/README.md with Japanese, English, Chinese, phone, and negative-number sample expectations
- [X] T046 Add or refresh generated sample files in docs/test-files/ for person and phone smoke testing
- [X] T047 Run full regression suite for tests/ with python -m pytest tests
- [X] T048 Run quickstart validation steps from specs/002-report-spacy-phone/quickstart.md
- [X] T049 Validate input file hashes remain unchanged for person and phone masking paths in tests/integration/test_input_hash_preservation.py
- [X] T050 Validate folder processing, unsupported skips, and language detection still pass with python -m pytest tests/integration/test_folder_discovery.py tests/integration/test_unsupported_skips.py tests/integration/test_folder_language_detection.py
- [X] T051 [P] Add regression test for repeated identical phone-number values reusing the same `PHONE_連番` in tests/integration/test_phone_masking_flow.py
- [X] T052 [P] Add UTF-8 BOM text-file regression covering detected terms, replacements, and report context in tests/integration/test_text_encoding_handling.py
- [X] T053 [P] Add language-separated sample inventory validation for English, Japanese, and Chinese folders in tests/integration/test_language_separated_samples.py
- [X] T054 Add CJK readability validation for Japanese and Chinese Office and text-based PDF samples in tests/integration/test_language_separated_samples.py
- [X] T055 [P] Update manual fixture documentation for repeated phone values, UTF-8 BOM, and CJK Office/PDF expectations in docs/test-files/README.md and docs/test-files/by-language/README.md
- [X] T056 Run focused validation for phone reuse, BOM handling, and language-separated sample checks with python -m pytest tests/integration/test_phone_masking_flow.py tests/integration/test_text_encoding_handling.py tests/integration/test_language_separated_samples.py
- [X] T057 Add single-file missing-language validation coverage in tests/unit/test_single_file_language_validation.py
- [X] T058 Run final full regression suite after polish validations with python -m pytest tests
- [X] T059 Add deterministic Chinese person-name fallback detection when the spaCy Chinese model is unavailable in src/masking_tool/detection/person.py and src/masking_tool_defaults/zh.yml
- [X] T060 Add Chinese person fallback unit and integration coverage in tests/unit/test_person_detector.py and tests/integration/test_person_masking_flow.py
- [X] T061 Reflect Chinese person fallback behavior in specs/002-report-spacy-phone/spec.md and related design documents
- [X] T062 [P] Add external communication permission guard data model and default-deny helper in src/masking_tool/core/external_permission.py
- [X] T063 [P] Add contract tests for default-deny and explicit-allow external communication behavior in tests/contract/test_external_communication_permission.py
- [X] T064 Wire external communication permission state into processing settings without changing local default behavior in src/masking_tool/core/models.py and src/masking_tool/core/processor.py
- [X] T065 [P] Update README.md with masking-run external communication permission behavior and dependency-installation boundary
- [X] T066 Run focused external communication permission validation with python -m pytest tests/contract/test_external_communication_permission.py
- [X] T067 Run final full regression suite after external communication permission tasks with python -m pytest tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; recommended MVP.
- **Phase 4 US2**: Depends on Phase 2; can proceed without US1 after report contract assumptions are stable.
- **Phase 5 US3**: Depends on Phase 2; can proceed without US1 or US2 after normalized match support exists.
- **Final Phase**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundation.
- **US2 (P2)**: Independent after foundation, but shares report output validation with US1.
- **US3 (P3)**: Independent after foundation, but shares normalized detection and conflict resolution with US2.

### Within Each User Story

- Write story tests first and confirm they fail.
- Implement source/model changes next.
- Integrate into processing flow.
- Run focused story tests before starting another story.

## Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001 is understood.
- T013, T014, and T015 can run in parallel for US1.
- T022 through T026 can run in parallel for US2.
- T034 through T038 can run in parallel for US3.
- T044 and T045 can run in parallel during polish.
- T051, T052, T053, T055, and T057 can run in parallel during polish because they touch separate validation or documentation files.
- T062, T063, and T065 can run in parallel during polish because they touch separate core, test, and documentation files.

## Parallel Example: User Story 1

```text
Task: "T013 [P] [US1] Add contract test for exactly 8 report columns and no audit columns in tests/contract/test_report_contract.py"
Task: "T014 [P] [US1] Add contract test for frozen header, filters, widths, wrapping, and risk/status row fills in tests/contract/test_report_display_formatting.py"
Task: "T015 [P] [US1] Add integration test for unsupported, no-replacement, and failed status-only rows using required columns in tests/integration/test_report_status_rows.py"
```

## Parallel Example: User Story 2

```text
Task: "T022 [P] [US2] Add unit tests for spaCy model loading, unavailable Japanese/English failure, and Chinese fallback behavior in tests/unit/test_person_detector.py"
Task: "T023 [P] [US2] Add unit tests for PERSON match normalization and deterministic replacement mapping in tests/unit/test_person_detection_matches.py"
Task: "T025 [P] [US2] Add integration test for Japanese and English person masking flow in tests/integration/test_person_masking_flow.py"
```

## Parallel Example: User Story 3

```text
Task: "T034 [P] [US3] Add unit tests for Japanese, US, and Chinese phone formats in tests/unit/test_phone_detector.py"
Task: "T035 [P] [US3] Add unit tests for phone false-positive exclusions in tests/unit/test_phone_false_positives.py"
Task: "T037 [P] [US3] Add integration test for phone masking and deterministic reruns in tests/integration/test_phone_masking_flow.py"
```

## Parallel Example: Polish Validation

```text
Task: "T051 [P] Add regression test for repeated identical phone-number values reusing the same PHONE_連番 in tests/integration/test_phone_masking_flow.py"
Task: "T052 [P] Add UTF-8 BOM text-file regression covering detected terms, replacements, and report context in tests/integration/test_text_encoding_handling.py"
Task: "T053 [P] Add language-separated sample inventory validation for English, Japanese, and Chinese folders in tests/integration/test_language_separated_samples.py"
Task: "T055 [P] Update manual fixture documentation for repeated phone values, UTF-8 BOM, and CJK Office/PDF expectations in docs/test-files/README.md and docs/test-files/by-language/README.md"
Task: "T057 Add single-file missing-language validation coverage in tests/unit/test_single_file_language_validation.py"
```

## Parallel Example: External Communication Permission

```text
Task: "T062 [P] Add external communication permission guard data model and default-deny helper in src/masking_tool/core/external_permission.py"
Task: "T063 [P] Add contract tests for default-deny and explicit-allow external communication behavior in tests/contract/test_external_communication_permission.py"
Task: "T065 [P] Update README.md with masking-run external communication permission behavior and dependency-installation boundary"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 only.
3. Validate US1 independently by opening `機密情報検出結果.xlsx` and running focused report tests.

### Incremental Delivery

1. Deliver US1 report contract and display improvements.
2. Add US2 person detection and required-model failure handling.
3. Add US3 phone detection and numeric false-positive controls.
4. Add polish validations for repeated phone-number reuse, UTF-8 BOM handling, and language-separated CJK samples.
5. Add external communication permission guard and tests.
6. Run full regression and quickstart validation.

### Notes

- Tasks marked [P] touch separate files or are test-only tasks that can be prepared independently.
- Do not add audit columns back to the workbook.
- Keep all accepted detections on the `検出語句` -> `置換提案` contract.
- Avoid OCR, image text, scanned PDF, and embedded-object scope expansion.
- Standard validation samples should stay language-separated; mixed-language files are stress-test inputs only.
