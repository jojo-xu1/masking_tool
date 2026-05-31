# Contract: Processing Workflow

## User Inputs

| Field | Single File | Folder |
|-------|-------------|--------|
| Input path | Required file path | Required folder path |
| Language | Required `en`, `ja`, or `zh` | Auto-detected per supported file |
| Rule settings | Required effective rule set | Required effective rule set |
| Output root | Defaults to `output` | Defaults to `output` |

## Run Output Layout

```text
output/
└── YYYYMMDD-HHMMSS/
    ├── 機密情報検出結果.xlsx
    └── files/
        └── <input-relative-paths>
```

If `YYYYMMDD-HHMMSS` already exists, append a deterministic suffix such as `_001`.

## Status Values

| Status | Meaning |
|--------|---------|
| `processed` | At least one replacement was written |
| `no_replacement` | File was supported but no enabled rule matched |
| `skipped_unsupported` | Extension is outside `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf` |
| `skipped_out_of_scope` | File requires OCR/image/embedded-object handling or is non-text PDF |
| `failed` | File could not be read, parsed, replaced, or written |

## Determinism Requirements

For identical inputs, settings, and applied languages:
- Detection rows are sorted deterministically.
- `カテゴリ_連番` assignments are identical.
- Replaced text is identical.
- Report values are identical except for run timestamp/output path metadata.

## Safety Requirements

- Never write to the original input path.
- Continue folder processing after per-file failures.
- Record every unsupported or failed file in the report.
- Treat embedded object content as out of scope.
- Treat scanned/image-only PDF content as out of scope.
