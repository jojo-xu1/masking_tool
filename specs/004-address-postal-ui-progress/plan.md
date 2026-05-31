# Implementation Plan: 行単位文脈・住所郵便番号マスク・UI進捗改善

**Branch**: `004-address-postal-ui-progress` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-address-postal-ui-progress/spec.md`

## Summary

Add line-based original context to report rows, ensure every accepted detection on the same line is reported and replaced, add configurable address and postal-code detection for representative Japan, US, and China formats, and improve the desktop UI so users see progress, duplicate-run protection, and completion summaries during file/folder masking. The implementation extends the existing Python masking pipeline and default rule model while preserving the required eight-column Excel report, per-run `output` layout, input non-destruction, supported extension scope, language validation/failure behavior, and OCR/image exclusions.

## Technical Context

**Language/Version**: Python >=3.11

**Primary Dependencies**: openpyxl, PyYAML, python-docx, python-pptx, PyMuPDF, lingua-language-detector, PySide6, spaCy model packages already used by existing person detection

**Storage**: Local files only; no database

**Testing**: pytest with unit, contract, and integration tests

**Target Platform**: Local Windows desktop/workstation use, with CLI-compatible core code

**Project Type**: Python masking tool with desktop UI, reusable core pipeline, and file-format adapters

**Performance Goals**: UI must show visible progress within 1 second of starting a folder run; line-context and address/postal detection must remain practical for the existing language-separated sample folders

**Constraints**: Local masking execution by default; no external transmission of input content, detected terms, replacement suggestions, or report content unless explicitly permitted; never overwrite input files; preserve required Excel report columns and risk coloring; address detection is limited to labels or clear country-specific structures; default address/postal country scope is Japanese/Japan, English/US, Chinese/China; single-file processing fails validation before processing when language is missing or unsupported; folder-mode files with undetectable language are marked `failed`, not masked, and reported with reasons

**Scale/Scope**: Existing supported extensions only: `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`; no OCR, image text, scanned PDF, or embedded-object processing

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope gate: PASS. Plan remains limited to `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`; unsupported extensions remain `skipped_unsupported`.
- Exclusion gate: PASS. Image text, scanned PDFs, embedded objects, and OCR remain out of scope.
- Replacement gate: PASS. Address and postal-code detections produce `検出語句` -> `置換提案` records using `ADDRESS_連番` and `POSTAL_CODE_連番`; all added sources are configuration-controlled, auditable, deterministic, and covered by report reasons.
- Output gate: PASS. Masked files remain under per-run `output` directories and inputs are never overwritten.
- Report gate: PASS. `機密情報検出結果.xlsx` keeps exactly the required columns: `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, `推奨対応`, with risk-level coloring.
- Configuration gate: PASS. Existing regex, explicit, person, and phone rules remain configurable; address and postal-code detection are added as configurable on/off detection sources in English, Japanese, and Chinese defaults; single-file language selection remains mandatory; folder-mode language-undetectable files fail visibly without replacement.
- Verification gate: PASS. Tests will cover reproducibility, same-line multi-detection, line-based original context, address/postal country rules, postal false positives, single-file language validation, folder language-undetectable failure, folder processing, unsupported skips, report integrity, UI progress behavior, and input non-destruction.

## Project Structure

### Documentation (this feature)

```text
specs/004-address-postal-ui-progress/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── detection-contract.md
│   ├── report-contract.md
│   └── ui-contract.md
└── tasks.md              # Created by /speckit-tasks
```

### Source Code (repository root)

```text
src/
├── masking_tool/
│   ├── core/
│   ├── config/
│   ├── detection/
│   ├── formats/
│   ├── replacement/
│   ├── reporting/
│   └── ui/
├── masking_tool_defaults/
│   ├── en.yml
│   ├── ja.yml
│   └── zh.yml
└── masking_tool.egg-info/

tests/
├── contract/
├── integration/
├── unit/
└── fixtures/
```

**Structure Decision**: Use the existing single Python package. Add address/postal detection under `src/masking_tool/detection/`, update default rule configuration under `src/masking_tool_defaults/`, update line-context generation in the detection/reporting path, extend UI progress behavior under `src/masking_tool/ui/`, and keep tests in the existing `tests/unit`, `tests/contract`, and `tests/integration` layout.

## Phase 0: Research

See [research.md](research.md). All technical unknowns are resolved:

- line-based original context and same-line multiple detections
- address detection scope and false-positive boundaries
- postal-code country rules and negative examples
- adjacent postal-code and address replacement behavior
- single-file language validation and folder language-undetectable failure handling
- UI progress state and duplicate-run prevention
- report and output compatibility for supported formats

## Phase 1: Design & Contracts

See:

- [data-model.md](data-model.md)
- [contracts/detection-contract.md](contracts/detection-contract.md)
- [contracts/report-contract.md](contracts/report-contract.md)
- [contracts/ui-contract.md](contracts/ui-contract.md)
- [quickstart.md](quickstart.md)

## Constitution Check Post-Design

- Scope gate: PASS. Design artifacts preserve supported extensions and unsupported skip behavior.
- Exclusion gate: PASS. No artifact introduces OCR, image text, scanned PDF, or embedded-object handling.
- Replacement gate: PASS. Contracts require `検出語句` -> `置換提案` for every accepted address/postal detection and define deterministic replacement reuse.
- Output gate: PASS. Quickstart verifies output under per-run `output` without input overwrite.
- Report gate: PASS. Report contract keeps exactly 8 columns and requires pre-replacement line context.
- Configuration gate: PASS. Data model and contracts include on/off state, language/country scope for address and postal-code detection, and explicit language validation/failure behavior.
- Verification gate: PASS. Quickstart and planned tests cover same-line multi-detection, line context, false positives, UI progress, reproducibility, report integrity, single-file language validation, folder language-undetectable failure, unsupported skips, and input safety.

## Complexity Tracking

No constitution violations or complexity exceptions.
