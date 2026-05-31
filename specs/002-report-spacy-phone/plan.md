# Implementation Plan: レポート表示改善と人名・電話番号マスク

**Branch**: `002-report-spacy-phone` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-report-spacy-phone/spec.md`

## Summary

Improve `機密情報検出結果.xlsx` readability while preserving the required 8-column report contract, add configurable person-name detection backed by spaCy for Japanese and English with Chinese fallback detection when the Chinese spaCy model is unavailable, and add default phone-number detection for representative Japanese, US, and Chinese formats. The implementation extends the existing Python masking pipeline by adding detection sources that produce the same `検出語句` -> `置換提案` records used by regex and explicit rules, including deterministic reuse of the same `PHONE_連番` for repeated phone-number values in a run. Masking execution is local by default; masking-related content may be sent externally only when the user explicitly permits that communication.

## Technical Context

**Language/Version**: Python >=3.11

**Primary Dependencies**: openpyxl, PyYAML, python-docx, python-pptx, PyMuPDF, lingua-language-detector, PySide6, spaCy with English/Japanese model packages and optional Chinese model package `zh_core_web_sm`

**Storage**: Local files only; no database

**Testing**: pytest with unit, contract, and integration tests

**Target Platform**: Local Windows desktop/workstation use, with CLI-compatible core code

**Project Type**: Python masking tool with desktop UI, reusable core pipeline, and file-format adapters

**Performance Goals**: Preserve existing folder processing behavior and keep report generation practical for representative fixture folders; person-name and phone-number replacement suggestions must be deterministic for identical inputs and settings

**Constraints**: Local masking execution by default after dependencies/models are installed; no external transmission of input content, detected terms, replacement suggestions, or report content unless explicitly permitted by the user; never overwrite input files; preserve required Excel report columns; fail visibly when enabled Japanese/English person detection cannot run; UTF-8 BOM and CJK text in validation samples must remain readable in extracted text and report context

**Scale/Scope**: Existing supported extensions only: `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`; no OCR, image text, scanned PDF, or embedded-object processing

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope gate: PASS. Plan remains limited to `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`; unsupported extensions remain `skipped_unsupported`.
- Exclusion gate: PASS. Image text, scanned PDFs, embedded objects, and OCR remain out of scope.
- Replacement gate: PASS. Person and phone detections produce `検出語句` -> `置換提案` records using `PERSON_連番` and `PHONE_連番`; spaCy person detection is explicitly listed with language scope, on/off control, unavailable-source behavior, conflict handling, and audit/report behavior.
- Output gate: PASS. Masked files remain under per-run `output/YYYYMMDD-HHMMSS/` output directories and inputs are never overwritten.
- Report gate: PASS. `機密情報検出結果.xlsx` keeps exactly the required columns: `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, `推奨対応`, with risk-level coloring.
- Configuration gate: PASS. Existing regex and explicit rules remain configurable; person and phone detection are on/off configurable; the explicitly specified ML/NER detection source is configuration-controlled; default English/Japanese/Chinese rule files remain in scope; single-file language selection and folder language handling remain unchanged.
- Verification gate: PASS. Tests will cover reproducibility, folder processing, unsupported skips, report integrity, input non-destruction, person detection, phone detection, repeated phone-number mapping, UTF-8 BOM handling, CJK-readable validation samples, explicit external-communication permission, and false-positive numeric examples.

## Project Structure

### Documentation (this feature)

```text
specs/002-report-spacy-phone/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── detection-contract.md
│   └── report-contract.md
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

**Structure Decision**: Use the existing single Python package. Add detection modules and tests under `src/masking_tool/detection/` and `tests/`, update default rule configuration under `src/masking_tool_defaults/`, update report formatting in `src/masking_tool/reporting/excel_report.py`, and keep UI changes scoped to configuration/status presentation in `src/masking_tool/ui/` only if needed.

## Phase 0: Research

See [research.md](research.md). All technical unknowns are resolved:

- spaCy model loading, unavailable-model behavior, and Chinese fallback behavior
- person-name detection source integration
- phone-number matching scope and false-positive controls
- deterministic phone-number replacement reuse
- language-separated validation samples and CJK/BOM handling
- external communication permission for masking-related content
- required 8-column Excel report layout
- deterministic conflict resolution and replacement numbering

## Phase 1: Design & Contracts

See:

- [data-model.md](data-model.md)
- [contracts/detection-contract.md](contracts/detection-contract.md)
- [contracts/report-contract.md](contracts/report-contract.md)
- [quickstart.md](quickstart.md)

## Constitution Check Post-Design

- Scope gate: PASS. Design artifacts preserve supported extensions and unsupported skip behavior.
- Exclusion gate: PASS. No artifact introduces OCR, image text, scanned PDF, or embedded-object handling.
- Replacement gate: PASS. Contracts require `検出語句` -> `置換提案` for every accepted detection and define spaCy person detection availability behavior.
- Output gate: PASS. Quickstart verifies output under per-run `output` without input overwrite.
- Report gate: PASS. Report contract requires exactly 8 columns, freeze pane, filters, wrapping, and row coloring.
- Configuration gate: PASS. Data model and contracts include on/off state for person and phone detection and source-level availability behavior for ML/NER detection.
- Verification gate: PASS. Quickstart and planned tests cover reproducibility, report integrity, unsupported skips, repeated phone-number mapping, UTF-8 BOM and CJK validation samples, false positives, explicit external-communication permission, and input safety.

## Complexity Tracking

No constitution violations or complexity exceptions.
