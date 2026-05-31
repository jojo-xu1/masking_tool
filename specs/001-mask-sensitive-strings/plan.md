# Implementation Plan: 機密文字列マスキング

**Branch**: `001-mask-sensitive-strings` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-mask-sensitive-strings/spec.md`

## Summary

Build a local Python desktop masking tool that accepts either a single file or a folder, detects confidential strings from enabled regex and explicit rules, generates `機密情報検出結果.xlsx`, and writes masked files to a per-run `output/YYYYMMDD-HHMMSS/` folder. The first release supports `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf` files only; image text, scanned PDFs, embedded objects, and OCR remain out of scope.

The implementation will separate UI, rule loading, discovery, detection, replacement, report generation, and format-specific document adapters so that the safety and reproducibility gates can be tested without driving the GUI.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: PySide6 for desktop UI; openpyxl for `.xlsx` and Excel report output; python-docx for `.docx`; python-pptx for `.pptx`; PyMuPDF for text-based `.pdf`; lingua-language-detector for offline English/Japanese/Chinese folder-mode language detection; PyYAML for rule configuration; pytest for tests.

**Storage**: Local filesystem only. Inputs remain unchanged; outputs are written under `output/YYYYMMDD-HHMMSS/` with deterministic collision suffixes when needed.

**Testing**: pytest with unit tests for rule resolution and replacement mapping, contract tests for config/report schemas, and integration tests using small text, Office, and text-based PDF fixtures.

**Target Platform**: Local desktop environment on Windows first, with path handling kept cross-platform where library support allows.

**Project Type**: Python desktop masking tool with a reusable core processing library.

**Performance Goals**: Process a folder of at least 20 mixed files and generate report artifacts within 3 minutes for normal office-sized documents; continue processing remaining files after per-file failures.

**Constraints**: No OCR, no scanned PDF recognition, no embedded-object processing, no input-file overwrite, deterministic output for the same inputs/settings/applied languages, and offline rule execution.

**Scale/Scope**: First release targets individual user runs over local files/folders, with tens to low hundreds of files per run and English/Japanese/Chinese rule sets.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope gate: PASS. Supported extensions are `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf`; unsupported extensions are recorded as `skipped_unsupported`.
- Exclusion gate: PASS. Image text, scanned PDFs, embedded objects, and OCR are explicitly out of scope and reported as skipped out of scope or failed with reason when encountered.
- Replacement gate: PASS. The generated `機密情報検出結果.xlsx` supplies `検出語句` and `置換提案`; replacement suggestions use deterministic `カテゴリ_連番` values.
- Output gate: PASS. Masked files are written under per-run `output/YYYYMMDD-HHMMSS/` folders, with collision-safe suffixes; input files are never overwritten.
- Report gate: PASS. The Excel report preserves `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, and `推奨対応`, plus processing metadata needed by the spec.
- Configuration gate: PASS. The design includes regex and explicit rules, on/off state, English/Japanese/Chinese defaults, single-file explicit language selection, and folder-mode language auto-detection.
- Verification gate: PASS. Tests cover reproducibility, folder-wide processing, unsupported skips, report integrity, output placement, language handling, rule conflicts, and input non-destruction.

**Post-Design Recheck**: PASS. Research, data model, contracts, and quickstart preserve every gate. Folder-mode language auto-detection is a clarified feature decision; single-file processing still requires explicit language selection.

## Project Structure

### Documentation (this feature)

```text
specs/001-mask-sensitive-strings/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── configuration-contract.md
│   ├── processing-contract.md
│   └── report-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── masking_tool/
│   ├── app.py                 # desktop application entry point
│   ├── ui/                    # file/folder picker, language selector, progress, results view
│   ├── core/                  # orchestration, run context, status model
│   ├── detection/             # regex/explicit matching, language selection, conflict resolution
│   ├── replacement/           # deterministic category sequence mapping and text replacement
│   ├── formats/               # txt/csv/log/docx/xlsx/pptx/pdf adapters
│   ├── reporting/             # Excel report generation and risk row coloring
│   └── config/                # schema loading and default rule sets
├── masking_tool_defaults/
│   ├── en.yml
│   ├── ja.yml
│   └── zh.yml
└── __main__.py

tests/
├── contract/
├── fixtures/
│   ├── text/
│   ├── office/
│   └── pdf/
├── integration/
└── unit/
```

**Structure Decision**: Use a single Python package with GUI and core logic separated. Format adapters isolate risky document mutation paths, while contract/integration tests exercise the core without requiring manual UI actions.

## Complexity Tracking

No constitution violations require justification.
