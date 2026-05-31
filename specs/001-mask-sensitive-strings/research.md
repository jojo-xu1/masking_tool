# Research: 機密文字列マスキング

## Decision: Use a local Python desktop app with a testable core library

**Rationale**: The feature requires screen-based file/folder selection and local document processing. A desktop app avoids uploading confidential documents and lets the core masking pipeline be tested independently from the UI.

**Alternatives considered**:
- CLI only: simpler, but does not satisfy screen operation.
- Web app: richer UI options, but increases deployment and data exposure concerns for local confidential files.

## Decision: Use PySide6 for the UI

**Rationale**: The app needs file/folder pickers, explicit language selection for single-file mode, progress, completion status, and report/output links. PySide6 supports a conventional desktop workflow while keeping the processing core independent.

**Alternatives considered**:
- Tkinter: available in the standard library, but weaker for a polished multi-step desktop workflow.
- Text UI: does not satisfy the stated screen-operation need.

## Decision: Store rule configuration as YAML

**Rationale**: Rule sets need enabled flags, language, category, risk level, rule type, pattern or literal value, recommendation text, and ordering. YAML is readable for Japanese/English/Chinese rule sets and supports comments in default files.

**Alternatives considered**:
- JSON: strict and easy to parse, but less friendly for manually maintained rule files.
- Excel configuration: familiar to users, but harder to diff, review, and validate deterministically.

## Decision: Generate `機密情報検出結果.xlsx` before replacement

**Rationale**: Clarification selected tool-generated detection results. The generated rows become the authoritative `検出語句` -> `置換提案` mapping for the same run, making report and replacement behavior traceable.

**Alternatives considered**:
- Require a pre-existing detection Excel input: rejected by clarification.
- Generate report only after replacement: loses a clear pre-replacement mapping contract.

## Decision: Use deterministic `カテゴリ_連番` replacement suggestions

**Rationale**: The selected replacement format is irreversible, easy to read, and classification-labeled. Deterministic ordering by file path, location, detection span, category, and rule order keeps repeated runs stable.

**Alternatives considered**:
- Hash suffixes: stable but less readable for review.
- Fixed category tokens: simple but cannot distinguish multiple unique values in the same category.

## Decision: Resolve rule conflicts by explicit rule, risk, then configuration order

**Rationale**: Explicit rules capture the strongest user intent. Risk priority favors conservative handling, and configuration order gives a deterministic final tie-breaker.

**Alternatives considered**:
- First match only: deterministic but can hide higher-risk matches.
- Mark all conflicts for manual review: safer but blocks first-version automation.

## Decision: Use format adapters per supported extension

**Rationale**: Text, CSV/log, Office XML-based documents, and PDFs have different mutation constraints. Per-format adapters keep scope boundaries visible and allow adapter-specific tests for input non-destruction.

**Alternatives considered**:
- Plain byte replacement across all files: unsafe for Office/PDF binary structures.
- Convert everything to text and rebuild files: loses formatting and document structure.

## Decision: Use PyMuPDF for text-based PDF replacement only

**Rationale**: Text-based PDFs require locating text spans and writing a modified PDF. PyMuPDF supports text search and redaction/overlay-style workflows suitable for a v1 text-PDF-only constraint. If replacement cannot be safely applied, the file is marked failed or skipped out of scope with a reason.

**Alternatives considered**:
- OCR-based processing: explicitly out of scope.
- Extract-to-text only: would not produce a replaced PDF artifact.

## Decision: Use offline language detection for folder mode

**Rationale**: Folder processing must determine language per file. Offline detection avoids sending document text to external services and aligns with confidential-file handling. Single-file mode remains explicit language selection.

**Alternatives considered**:
- One language per folder: simpler, but rejected by clarification.
- Cloud language detection: adds privacy and availability concerns.

## Decision: Use pytest and fixture-based verification

**Rationale**: Reproducibility, file non-destruction, skipped unsupported files, report columns/colors, and per-format behavior need automated validation. Small fixtures keep the tests fast and deterministic.

**Alternatives considered**:
- Manual quickstart validation only: insufficient for safety and reproducibility gates.
