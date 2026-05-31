# Tasks: 機密文字列マスキング

**Input**: Design documents from `/specs/001-mask-sensitive-strings/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/

**Tests**: Required by constitution gates for masking replacement, supported file handling, unsupported skips, folder-wide processing, report integrity, output placement, language handling, configuration on/off behavior, reproducibility, and input non-destruction.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundations are complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another incomplete task in the same phase
- **[Story]**: User story label for story phases only
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python desktop app package, dependency metadata, and test layout.

- [X] T001 Create Python package directories in `src/masking_tool/`, `src/masking_tool_defaults/`, `tests/unit/`, `tests/contract/`, `tests/integration/`, and `tests/fixtures/`
- [X] T002 Create project metadata and dependencies in `pyproject.toml`
- [X] T003 Create package entry point in `src/masking_tool/__main__.py`
- [X] T004 [P] Create application entry stub in `src/masking_tool/app.py`
- [X] T005 [P] Create pytest configuration in `pytest.ini`
- [X] T006 [P] Create developer setup notes in `README.md`

**Checkpoint**: Project can install in editable mode and import `masking_tool`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared contracts, models, configuration loading, deterministic run context, and test fixtures needed by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

### Foundational Tests

- [X] T007 [P] Add configuration schema contract tests in `tests/contract/test_configuration_contract.py`
- [X] T008 [P] Add processing status contract tests in `tests/contract/test_processing_contract.py`
- [X] T009 [P] Add report workbook contract tests in `tests/contract/test_report_contract.py`
- [X] T010 [P] Add replacement determinism unit tests in `tests/unit/test_replacement_mapping.py`
- [X] T011 [P] Add rule conflict priority unit tests in `tests/unit/test_rule_conflicts.py`

### Foundational Implementation

- [X] T012 Create domain enums and dataclasses in `src/masking_tool/core/models.py`
- [X] T013 Create processing result and error types in `src/masking_tool/core/status.py`
- [X] T014 Create deterministic run output path builder in `src/masking_tool/core/output.py`
- [X] T015 Create orchestration shell in `src/masking_tool/core/processor.py`
- [X] T016 Create YAML configuration loader and validator in `src/masking_tool/config/loader.py`
- [X] T017 Create default English rules in `src/masking_tool_defaults/en.yml`
- [X] T018 Create default Japanese rules in `src/masking_tool_defaults/ja.yml`
- [X] T019 Create default Chinese rules in `src/masking_tool_defaults/zh.yml`
- [X] T020 Create rule matching and conflict resolution engine in `src/masking_tool/detection/rules.py`
- [X] T021 Create deterministic `カテゴリ_連番` replacement mapper in `src/masking_tool/replacement/mapping.py`
- [X] T022 Create report workbook builder with required columns and risk colors in `src/masking_tool/reporting/excel_report.py`
- [X] T023 Create fixture rule files in `tests/fixtures/rules/`
- [X] T024 Create shared fixture helpers in `tests/fixtures/conftest.py`

**Checkpoint**: Configuration contracts, conflict resolution, replacement mapping, output path safety, and report shape are testable without document adapters or UI.

---

## Phase 3: User Story 1 - 単一ファイルをマスキングする (Priority: P1) MVP

**Goal**: Select one supported file, select a language, generate `機密情報検出結果.xlsx`, and write a masked file under `output/YYYYMMDD-HHMMSS/` without modifying the original.

**Independent Test**: Run the single-file processing core against a supported fixture with enabled rules and verify report rows, `カテゴリ_連番` replacements, per-run output placement, and unchanged input.

### Tests for User Story 1

- [X] T025 [P] [US1] Add single-file text replacement integration test in `tests/integration/test_single_file_text_flow.py`
- [X] T026 [P] [US1] Add single-file output non-destruction integration test in `tests/integration/test_single_file_input_safety.py`
- [X] T027 [P] [US1] Add generated Excel report integration test in `tests/integration/test_single_file_report.py`
- [X] T028 [P] [US1] Add single-file language validation test in `tests/unit/test_single_file_language_validation.py`

### Implementation for User Story 1

- [X] T029 [US1] Implement input selection validation for single-file mode in `src/masking_tool/core/input_selection.py`
- [X] T030 [US1] Implement target file discovery for single-file mode in `src/masking_tool/core/discovery.py`
- [X] T031 [US1] Implement plain text, CSV, and log adapter in `src/masking_tool/formats/text_adapter.py`
- [X] T032 [US1] Implement detection result generation for one target file in `src/masking_tool/detection/detector.py`
- [X] T033 [US1] Implement text replacement application from generated detection rows in `src/masking_tool/replacement/apply.py`
- [X] T034 [US1] Connect single-file pipeline in `src/masking_tool/core/processor.py`
- [X] T035 [US1] Implement minimal desktop file-mode UI in `src/masking_tool/ui/main_window.py`
- [X] T036 [US1] Wire PySide6 application startup to the main window in `src/masking_tool/app.py`
- [X] T037 [US1] Add single-file sample fixtures in `tests/fixtures/text/`

**Checkpoint**: User Story 1 is complete when a single `.txt`, `.csv`, or `.log` fixture can be processed with generated report and masked output while the source file remains unchanged.

---

## Phase 4: User Story 2 - フォルダ内の対象ファイルを一括マスキングする (Priority: P2)

**Goal**: Select a folder, auto-detect language per supported file, process all supported files including subfolders, and record unsupported/out-of-scope/failed files in the report.

**Independent Test**: Run folder processing against a fixture tree containing mixed supported files, unsupported files, multilingual files, and out-of-scope PDF fixtures; verify per-file statuses and continued processing after failures.

### Tests for User Story 2

- [X] T038 [P] [US2] Add recursive folder discovery integration test in `tests/integration/test_folder_discovery.py`
- [X] T039 [P] [US2] Add unsupported extension reporting integration test in `tests/integration/test_unsupported_skips.py`
- [X] T040 [P] [US2] Add folder language auto-detection integration test in `tests/integration/test_folder_language_detection.py`
- [X] T041 [P] [US2] Add per-file failure continuation integration test in `tests/integration/test_folder_failure_continuation.py`
- [X] T042 [P] [US2] Add Office and text-based PDF adapter smoke tests in `tests/integration/test_document_adapters.py`

### Implementation for User Story 2

- [X] T043 [US2] Extend target file discovery for recursive folder mode in `src/masking_tool/core/discovery.py`
- [X] T044 [US2] Implement unsupported and out-of-scope status classification in `src/masking_tool/core/eligibility.py`
- [X] T045 [US2] Implement offline language detection wrapper for folder mode in `src/masking_tool/detection/language.py`
- [X] T046 [US2] Implement `.docx` adapter in `src/masking_tool/formats/docx_adapter.py`
- [X] T047 [US2] Implement `.xlsx` adapter in `src/masking_tool/formats/xlsx_adapter.py`
- [X] T048 [US2] Implement `.pptx` adapter in `src/masking_tool/formats/pptx_adapter.py`
- [X] T049 [US2] Implement text-based `.pdf` adapter and out-of-scope detection in `src/masking_tool/formats/pdf_adapter.py`
- [X] T050 [US2] Connect folder processing loop and per-file failure handling in `src/masking_tool/core/processor.py`
- [X] T051 [US2] Extend report rows for unsupported, out-of-scope, no-replacement, and failed files in `src/masking_tool/reporting/excel_report.py`
- [X] T052 [US2] Extend desktop UI with folder mode, progress, and result summary in `src/masking_tool/ui/main_window.py`
- [X] T053 [US2] Add mixed folder fixtures in `tests/fixtures/folders/`
- [X] T054 [US2] Add Office and PDF fixtures in `tests/fixtures/office/` and `tests/fixtures/pdf/`

**Checkpoint**: User Story 2 is complete when folder processing creates one per-run output folder, processes all eligible files, records every unsupported or failed file, and keeps going after per-file failures.

---

## Phase 5: User Story 3 - 設定ファイルでマスク対象を管理する (Priority: P3)

**Goal**: Allow users to manage regex and explicit rules, toggle common rules on/off, and apply English/Japanese/Chinese defaults consistently.

**Independent Test**: Change rule enabled flags and language rule files, process the same fixture, and verify only enabled rules for the applied language affect detections, replacements, and report rows.

### Tests for User Story 3

- [X] T055 [P] [US3] Add rule on/off behavior integration test in `tests/integration/test_rule_toggle_behavior.py`
- [X] T056 [P] [US3] Add language-specific default rule loading test in `tests/contract/test_default_language_rules.py`
- [X] T057 [P] [US3] Add explicit rule matching test in `tests/unit/test_explicit_rules.py`
- [X] T058 [P] [US3] Add regex rule matching test in `tests/unit/test_regex_rules.py`

### Implementation for User Story 3

- [X] T059 [US3] Implement effective rule set merge from defaults and user config in `src/masking_tool/config/effective_rules.py`
- [X] T060 [US3] Add user configuration file loading path to `src/masking_tool/config/loader.py`
- [X] T061 [US3] Implement rule toggle state model in `src/masking_tool/config/rule_state.py`
- [X] T062 [US3] Extend detector to filter rules by applied language and enabled state in `src/masking_tool/detection/detector.py`
- [X] T063 [US3] Add settings UI for rule files and on/off toggles in `src/masking_tool/ui/settings_panel.py`
- [X] T064 [US3] Connect settings panel to main window processing options in `src/masking_tool/ui/main_window.py`
- [X] T065 [US3] Document default rule maintenance in `docs/rules.md`

**Checkpoint**: User Story 3 is complete when users can toggle regex/explicit rules and see deterministic changes in generated detection rows and masked output.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete constitution verification, quickstart validation, and developer quality gates across all user stories.

- [X] T066 [P] Add reproducibility regression test for repeated runs in `tests/integration/test_reproducibility.py`
- [X] T067 [P] Add report row color validation test in `tests/contract/test_report_risk_colors.py`
- [X] T068 [P] Add original input hash preservation test across success and failure cases in `tests/integration/test_input_hash_preservation.py`
- [X] T069 [P] Add quickstart validation script in `scripts/validate_quickstart.py`
- [X] T070 Update user-facing quickstart details in `specs/001-mask-sensitive-strings/quickstart.md`
- [X] T071 Update README usage instructions for desktop launch and test commands in `README.md`
- [X] T072 Run full pytest suite and record results in `specs/001-mask-sensitive-strings/test-results.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; establishes MVP single-file pipeline.
- **Phase 4 US2**: Depends on Phase 2 and reuses US1 core replacement/reporting behavior.
- **Phase 5 US3**: Depends on Phase 2 and integrates with US1/US2 detection behavior.
- **Phase 6 Polish**: Depends on the user stories being implemented.

### User Story Dependencies

- **US1 (P1)**: Start after Phase 2; no dependency on US2 or US3.
- **US2 (P2)**: Start after Phase 2; can proceed in parallel with US3, but final folder flow benefits from US1 pipeline completion.
- **US3 (P3)**: Start after Phase 2; can proceed in parallel with US2, then integrate settings into the shared detector.

### Within Each User Story

- Tests before implementation.
- Models/config/status before services and adapters.
- Adapters before full processor integration.
- Processor integration before UI wiring.
- Each story must pass its independent test before moving to the next priority in a sequential workflow.

---

## Parallel Execution Examples

### US1

```text
Run together after Phase 2:
- T025 [US1] tests/integration/test_single_file_text_flow.py
- T026 [US1] tests/integration/test_single_file_input_safety.py
- T027 [US1] tests/integration/test_single_file_report.py
- T028 [US1] tests/unit/test_single_file_language_validation.py
```

### US2

```text
Run together after Phase 2:
- T038 [US2] tests/integration/test_folder_discovery.py
- T039 [US2] tests/integration/test_unsupported_skips.py
- T040 [US2] tests/integration/test_folder_language_detection.py
- T041 [US2] tests/integration/test_folder_failure_continuation.py
- T042 [US2] tests/integration/test_document_adapters.py
```

### US3

```text
Run together after Phase 2:
- T055 [US3] tests/integration/test_rule_toggle_behavior.py
- T056 [US3] tests/contract/test_default_language_rules.py
- T057 [US3] tests/unit/test_explicit_rules.py
- T058 [US3] tests/unit/test_regex_rules.py
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 shared foundations.
3. Complete Phase 3 single-file text flow.
4. Validate generated report, output placement, deterministic replacements, and input non-destruction.

### Incremental Delivery

1. Deliver US1 for single-file `.txt`, `.csv`, and `.log` masking.
2. Add US2 folder discovery, language detection, Office/PDF adapters, and skip/failure reporting.
3. Add US3 rule management and settings UI.
4. Finish Phase 6 with reproducibility, quickstart, and full-suite validation.

### Team Parallelism

After Phase 2:
- One developer can implement US1 processor/UI.
- One developer can implement US2 adapters and folder handling.
- One developer can implement US3 configuration/settings.
- Contract tests and fixtures can be expanded in parallel because they target separate files.

---

## Notes

- `[P]` tasks are safe to run in parallel because they touch separate files.
- User story tasks include `[US1]`, `[US2]`, or `[US3]` for traceability.
- Contract and integration tests are required by the constitution and quickstart.
- Do not add OCR, image-text extraction, scanned-PDF recognition, or embedded-object processing in v1.
- Keep original inputs read-only; write only under the per-run output directory.
