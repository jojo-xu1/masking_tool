# Tasks: 行単位文脈・住所郵便番号マスク・UI進捗改善

**Input**: Design documents from `/specs/004-address-postal-ui-progress/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by constitution gates for masking replacement, supported file handling, unsupported skips, folder-wide processing, report integrity, output placement, language selection/detection behavior, configuration on/off behavior, reproducibility, UI progress behavior, and input non-destruction.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- All task descriptions include exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare fixtures, rule metadata, and test entry points shared by all stories.

- [X] T001 Add address and postal-code fixture values to English, Japanese, and Chinese language-separated sample definitions in scripts/generate_language_test_files.py
- [X] T002 [P] Add manual fixture expectations for address, postal-code, same-line detection, and UI progress smoke checks in docs/test-files/by-language/README.md
- [X] T003 [P] Add feature quickstart validation notes for address/postal and line-context behavior in docs/test-files/README.md
- [X] T004 [P] Add negative numeric and ambiguous address fixture text files in tests/fixtures/text/address_postal/
- [X] T005 Regenerate or refresh language-separated sample files under docs/test-files/by-language/ using scripts/generate_language_test_files.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared detection categories, configuration support, context helpers, and progress data that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T006 Extend RuleType or detection source support for address and postal-code sources in src/masking_tool/core/models.py
- [X] T007 [P] Add processing progress state model for UI and core callbacks in src/masking_tool/core/models.py
- [X] T008 Add line-context helper utilities for replaceable text blocks in src/masking_tool/detection/matches.py
- [X] T009 Update normalized DetectionMatch shape to carry pre-replacement line context in src/masking_tool/detection/matches.py
- [X] T010 Update conflict resolution to preserve existing priority while supporting address and postal-code matches in src/masking_tool/detection/rules.py
- [X] T011 Update rule configuration loading for address/postal source metadata and backward compatibility in src/masking_tool/config/loader.py
- [X] T012 Add address/postal source on/off state support in src/masking_tool/config/rule_state.py
- [X] T013 Add default address and postal-code metadata to src/masking_tool_defaults/en.yml, src/masking_tool_defaults/ja.yml, and src/masking_tool_defaults/zh.yml
- [X] T014 [P] Add unit tests for line-context helper and normalized match shape in tests/unit/test_detection_matches.py
- [X] T015 [P] Add contract tests for address/postal default rule metadata in tests/contract/test_default_language_rules.py

**Checkpoint**: Foundation ready. User story work can start independently.

---

## Phase 3: User Story 1 - 行単位の原文文脈で検出結果を確認する (Priority: P1) MVP

**Goal**: Report each accepted detection with the full original pre-replacement line as context, including multiple detections on the same line.

**Independent Test**: Process a file with multiple sensitive values on one line and confirm every value is replaced, every value gets a separate report row, and each row shows the same pre-replacement original line.

### Tests for User Story 1

- [X] T016 [P] [US1] Add contract test for pre-replacement full-line report context in tests/contract/test_report_line_context_contract.py
- [X] T017 [P] [US1] Add contract test for same-line multiple detection report rows in tests/contract/test_report_line_context_contract.py
- [X] T018 [P] [US1] Add unit tests for line context extraction around LF, CRLF, CSV rows, and log lines in tests/unit/test_detection_line_context.py
- [X] T019 [P] [US1] Add integration test for same-line multi-detection replacement in text files in tests/integration/test_line_context_replacement_flow.py
- [X] T020 [P] [US1] Add integration test for same-line multi-detection replacement in Office and text-based PDF files in tests/integration/test_line_context_document_flow.py

### Implementation for User Story 1

- [X] T021 [US1] Capture pre-replacement line context when building detection results in src/masking_tool/detection/detector.py
- [X] T022 [US1] Pass line context from DetectionMatch to DetectionResult in src/masking_tool/core/models.py and src/masking_tool/detection/detector.py
- [X] T023 [US1] Update report row generation to use DetectionResult line context without recomputing replaced context in src/masking_tool/reporting/excel_report.py
- [X] T024 [US1] Ensure block-based processor preserves same-line multiple detections and reverse-order replacement in src/masking_tool/core/processor.py
- [X] T025 [US1] Update text, CSV, and log integration expectations for full original line context in tests/integration/test_single_file_text_flow.py and tests/integration/test_supported_format_replacement_coverage.py
- [X] T026 [US1] Update Office/PDF integration expectations for pre-replacement line context in tests/integration/test_document_adapters.py and tests/integration/test_supported_format_replacement_coverage.py
- [X] T027 [US1] Run focused line-context validation with python -m pytest tests/contract/test_report_line_context_contract.py tests/unit/test_detection_line_context.py tests/integration/test_line_context_replacement_flow.py tests/integration/test_line_context_document_flow.py

**Checkpoint**: User Story 1 is independently functional and is the MVP.

---

## Phase 4: User Story 2 - 各国ルールに従って住所と郵便番号をマスクする (Priority: P2)

**Goal**: Detect and mask representative Japan, US, and China address/postal-code values using configurable defaults, while avoiding broad ambiguous address guessing and postal false positives.

**Independent Test**: Process English/US, Japanese/Japan, and Chinese/China samples containing address and postal-code values and confirm expected `ADDRESS_連番` and `POSTAL_CODE_連番` replacements with deterministic reuse.

### Tests for User Story 2

- [X] T028 [P] [US2] Add unit tests for Japanese postal-code positive and negative examples in tests/unit/test_postal_detector.py
- [X] T029 [P] [US2] Add unit tests for US ZIP positive and negative examples in tests/unit/test_postal_detector.py
- [X] T030 [P] [US2] Add unit tests for China postal-code positive and negative examples in tests/unit/test_postal_detector.py
- [X] T031 [P] [US2] Add unit tests for labeled and structurally clear address detection in tests/unit/test_address_detector.py
- [X] T032 [P] [US2] Add unit tests for ambiguous unlabeled location-like text not being address-masked in tests/unit/test_address_detector.py
- [X] T033 [P] [US2] Add unit tests for adjacent postal-code and address non-overlapping spans in tests/unit/test_address_postal_adjacency.py
- [X] T034 [P] [US2] Add contract tests for ADDRESS and POSTAL_CODE category/replacement behavior in tests/contract/test_address_postal_detection_contract.py
- [X] T035 [P] [US2] Add integration test for Japanese/Japan address and postal-code masking in tests/integration/test_address_postal_masking_flow.py
- [X] T036 [P] [US2] Add integration test for English/US address and ZIP masking in tests/integration/test_address_postal_masking_flow.py
- [X] T037 [P] [US2] Add integration test for Chinese/China address and postal-code masking in tests/integration/test_address_postal_masking_flow.py
- [X] T038 [P] [US2] Add integration test for disabling address/postal sources while preserving person and phone masking in tests/integration/test_address_postal_toggle_behavior.py
- [X] T039 [P] [US2] Add reproducibility test for repeated address and postal-code values in tests/integration/test_address_postal_reproducibility.py

### Implementation for User Story 2

- [X] T040 [US2] Implement postal-code detection for representative Japan, US, and China formats with negative filters in src/masking_tool/detection/postal.py
- [X] T041 [US2] Implement address detection for labels and clear country-specific structures in src/masking_tool/detection/address.py
- [X] T042 [US2] Integrate address and postal-code matches into detect_text before conflict resolution in src/masking_tool/detection/detector.py
- [X] T043 [US2] Ensure adjacent postal-code and address spans remain separate and non-overlapping in src/masking_tool/detection/address.py and src/masking_tool/detection/postal.py
- [X] T044 [US2] Ensure replacement mapping produces deterministic ADDRESS_連番 and POSTAL_CODE_連番 values in src/masking_tool/replacement/mapping.py
- [X] T045 [US2] Add address/postal categories, reasons, recommendations, and default enabled state to src/masking_tool_defaults/en.yml, src/masking_tool_defaults/ja.yml, and src/masking_tool_defaults/zh.yml
- [X] T046 [US2] Surface address and postal-code enabled/disabled state in UI settings in src/masking_tool/ui/settings_panel.py and src/masking_tool/ui/main_window.py
- [X] T047 [US2] Update language-separated generated fixtures with address/postal positives and negatives in scripts/generate_language_test_files.py
- [X] T048 [US2] Refresh docs/test-files/by-language/ fixtures and expectations for address/postal values in docs/test-files/by-language/README.md
- [X] T049 [US2] Run focused address/postal validation with python -m pytest tests/unit/test_postal_detector.py tests/unit/test_address_detector.py tests/unit/test_address_postal_adjacency.py tests/contract/test_address_postal_detection_contract.py tests/integration/test_address_postal_masking_flow.py tests/integration/test_address_postal_toggle_behavior.py tests/integration/test_address_postal_reproducibility.py

**Checkpoint**: User Story 2 works independently with existing report and replacement contracts.

---

## Phase 5: User Story 3 - 実行中の進捗をUIで確認する (Priority: P3)

**Goal**: Show visible run progress, prevent duplicate starts, and summarize processed/skipped/failed results in the desktop UI.

**Independent Test**: Run a multi-file folder from the UI and confirm progress appears within 1 second, duplicate run starts are blocked, and the completion summary includes output location and counts.

### Tests for User Story 3

- [X] T050 [P] [US3] Add contract tests for processing progress state fields and count transitions in tests/contract/test_ui_progress_contract.py
- [X] T051 [P] [US3] Add integration test for core processing progress callbacks during folder runs in tests/integration/test_processing_progress_flow.py
- [X] T052 [P] [US3] Add UI-level test or smoke harness for duplicate-run prevention in tests/integration/test_ui_progress_behavior.py
- [X] T053 [P] [US3] Add UI-level test or smoke harness for completion summary counts in tests/integration/test_ui_progress_behavior.py
- [X] T054 [P] [US3] Add UI progress timing test that verifies visible progress within 1 second of starting a folder run in tests/integration/test_ui_progress_behavior.py

### Implementation for User Story 3

- [X] T055 [US3] Add optional progress callback support to process() in src/masking_tool/core/processor.py
- [X] T056 [US3] Emit progress updates for discovered total, current target, completed targets, processed, skipped, and failed counts in src/masking_tool/core/processor.py
- [X] T057 [US3] Add progress bar and count labels to the desktop UI in src/masking_tool/ui/main_window.py
- [X] T058 [US3] Prevent duplicate run starts and restore runnable state after completion or failure in src/masking_tool/ui/main_window.py
- [X] T059 [US3] Add address/postal detection toggles to the UI detection controls in src/masking_tool/ui/main_window.py and src/masking_tool/ui/settings_panel.py
- [X] T060 [US3] Display output location, processed count, skipped count, failed count, and failure reasons in the UI completion log in src/masking_tool/ui/main_window.py
- [X] T061 [US3] Run focused UI progress validation with python -m pytest tests/contract/test_ui_progress_contract.py tests/integration/test_processing_progress_flow.py tests/integration/test_ui_progress_behavior.py

**Checkpoint**: User Story 3 works independently with core processing and desktop UI behavior.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Validate constitution gates, documentation, and full-system behavior after selected stories are complete.

- [X] T062 [P] Update README.md with address/postal detection scope, toggles, and UI progress behavior in README.md
- [X] T063 [P] Update docs/rules.md with address and postal-code default rule categories and country scope in docs/rules.md
- [X] T064 [P] Update quickstart validation notes after implementation in specs/004-address-postal-ui-progress/quickstart.md
- [X] T065 Validate unsupported files are still reported as skipped_unsupported with python -m pytest tests/integration/test_unsupported_skips.py
- [X] T066 Validate input file hashes remain unchanged for address/postal paths with python -m pytest tests/integration/test_input_hash_preservation.py
- [X] T067 Validate folder processing and language handling with python -m pytest tests/integration/test_folder_discovery.py tests/integration/test_folder_language_detection.py tests/integration/test_language_separated_samples.py
- [X] T068 Validate single-file missing or unsupported language fails before processing with python -m pytest tests/unit/test_single_file_language_validation.py tests/integration/test_single_file_input_safety.py
- [X] T069 Validate folder language-undetectable supported files are reported failed without masked output with python -m pytest tests/integration/test_folder_language_detection.py tests/integration/test_report_status_rows.py
- [X] T070 Validate required 8-column report layout and risk coloring with python -m pytest tests/contract/test_report_contract.py tests/contract/test_report_display_formatting.py tests/contract/test_report_risk_colors.py
- [X] T071 Run full regression suite with python -m pytest tests
- [X] T072 Run compile validation with python -m compileall src tests scripts
- [X] T073 Run manual smoke validation from specs/004-address-postal-ui-progress/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; recommended MVP.
- **Phase 4 US2**: Depends on Phase 2 and can proceed without US3, but benefits from US1 line-context support for full validation.
- **Phase 5 US3**: Depends on Phase 2 and can proceed after core progress state is available.
- **Final Phase**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundation; establishes report context and same-line multi-detection behavior.
- **US2 (P2)**: Independent after foundation for detection and replacement, with final report expectations using US1 context.
- **US3 (P3)**: Independent after foundation for UI progress and summary behavior.

### Within Each User Story

- Write story tests first and confirm they fail.
- Implement source/model changes next.
- Integrate into processing, reporting, or UI flow.
- Run focused story tests before starting another story.

## Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001 is understood.
- T007, T014, and T015 can run in parallel during foundation because they touch separate model/test files.
- T016 through T020 can run in parallel for US1 tests.
- T028 through T039 can run in parallel for US2 tests because they touch separate test scopes.
- T050 through T054 can run in parallel for US3 tests.
- T062, T063, and T064 can run in parallel during polish because they touch separate documentation files.

## Parallel Example: User Story 1

```text
Task: "T016 [P] [US1] Add contract test for pre-replacement full-line report context in tests/contract/test_report_line_context_contract.py"
Task: "T018 [P] [US1] Add unit tests for line context extraction around LF, CRLF, CSV rows, and log lines in tests/unit/test_detection_line_context.py"
Task: "T020 [P] [US1] Add integration test for same-line multi-detection replacement in Office and text-based PDF files in tests/integration/test_line_context_document_flow.py"
```

## Parallel Example: User Story 2

```text
Task: "T028 [P] [US2] Add unit tests for Japanese postal-code positive and negative examples in tests/unit/test_postal_detector.py"
Task: "T031 [P] [US2] Add unit tests for labeled and structurally clear address detection in tests/unit/test_address_detector.py"
Task: "T034 [P] [US2] Add contract tests for ADDRESS and POSTAL_CODE category/replacement behavior in tests/contract/test_address_postal_detection_contract.py"
Task: "T038 [P] [US2] Add integration test for disabling address/postal sources while preserving person and phone masking in tests/integration/test_address_postal_toggle_behavior.py"
```

## Parallel Example: User Story 3

```text
Task: "T050 [P] [US3] Add contract tests for processing progress state fields and count transitions in tests/contract/test_ui_progress_contract.py"
Task: "T051 [P] [US3] Add integration test for core processing progress callbacks during folder runs in tests/integration/test_processing_progress_flow.py"
Task: "T052 [P] [US3] Add UI-level test or smoke harness for duplicate-run prevention in tests/integration/test_ui_progress_behavior.py"
Task: "T054 [P] [US3] Add UI progress timing test that verifies visible progress within 1 second of starting a folder run in tests/integration/test_ui_progress_behavior.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 only.
3. Validate US1 independently by processing a same-line multi-detection sample and checking output replacements plus `機密情報検出結果.xlsx` line context.

### Incremental Delivery

1. Deliver US1 line-context and same-line multi-detection behavior.
2. Add US2 address and postal-code detection with country-specific defaults and false-positive controls.
3. Add US3 UI progress, duplicate-run guard, and completion summary.
4. Run full regression and quickstart validation.

### Notes

- Tasks marked [P] touch separate files or are test-only tasks that can be prepared independently.
- Keep all accepted detections on the `検出語句` -> `置換提案` contract.
- Do not add report columns.
- Do not broaden scope to OCR, image text, scanned PDFs, embedded objects, or global address parsing.
- Standard validation samples should stay language-separated.

