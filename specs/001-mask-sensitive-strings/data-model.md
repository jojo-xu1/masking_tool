# Data Model: 機密文字列マスキング

## InputSelection

Represents the user's processing target.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `selection_type` | enum | yes | `file` or `folder` |
| `input_path` | path | yes | Existing readable file or folder |
| `single_file_language` | enum | conditional | Required for `file`; one of `en`, `ja`, `zh` |
| `folder_language_mode` | enum | conditional | `auto_detect` for `folder` |
| `output_root` | path | yes | Defaults to project/user-selected `output` folder |

Validation:
- Single-file processing cannot start without a supported language.
- Folder processing uses per-file language auto-detection and does not accept a single folder-wide override in v1.

## ProcessingRun

Represents one execution.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `run_id` | string | yes | Timestamp `YYYYMMDD-HHMMSS` plus deterministic suffix on collision |
| `started_at` | datetime | yes | Local timestamp |
| `output_dir` | path | yes | `output/<run_id>/` |
| `settings_snapshot` | object | yes | Effective enabled rules used by the run |
| `status` | enum | yes | `completed`, `completed_with_failures`, `failed_validation` |

Validation:
- Existing output artifacts are never overwritten.
- The effective settings snapshot is stable for reproducibility reporting.

## TargetFile

Represents each discovered input file.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_path` | path | yes | Original file path |
| `relative_path` | path | yes | Relative to selected folder or filename for single file |
| `extension` | string | yes | Lowercase extension |
| `eligibility` | enum | yes | `supported`, `unsupported`, `out_of_scope` |
| `applied_language` | enum | conditional | Explicit or detected `en`, `ja`, `zh` |
| `language_confidence` | decimal | no | Used for folder-mode audit |
| `status` | enum | yes | `processed`, `no_replacement`, `skipped_unsupported`, `skipped_out_of_scope`, `failed` |
| `output_path` | path | no | Present when an output file is written |
| `failure_reason` | string | no | Required for failed/skipped out-of-scope files |

Validation:
- Unsupported extensions are never passed to format adapters.
- Failed files do not stop other files in the same folder run.

## MaskingRule

Represents one configured detection and masking rule.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Unique within all loaded rule files |
| `language` | enum | yes | `en`, `ja`, `zh` |
| `enabled` | boolean | yes | Disabled rules do not match |
| `rule_type` | enum | yes | `regex` or `explicit` |
| `pattern` | string | conditional | Required for `regex` |
| `literal` | string | conditional | Required for `explicit` |
| `category` | string | yes | Used in `カテゴリ_連番` |
| `risk_level` | enum | yes | `high`, `medium`, `low` |
| `judgment_reason` | string | yes | Report value |
| `recommended_action` | string | yes | Report value |
| `order` | integer | yes | Configuration order for tie-breaking |

Validation:
- Regex patterns must compile before processing.
- Rule conflict priority is explicit rule first, then higher risk, then lower `order`.

## DetectionResult

Represents one selected detection result row before replacement.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `no` | integer | yes | Stable row number in report |
| `target_file_id` | reference | yes | Links to `TargetFile` |
| `rule_id` | reference | yes | Winning rule |
| `detected_text` | string | yes | `検出語句` |
| `replacement` | string | yes | `置換提案`, `カテゴリ_連番` |
| `context` | string | yes | `原文または前後の文脈` |
| `category` | string | yes | `情報カテゴリ` |
| `risk_level` | enum | yes | `リスクレベル` |
| `judgment_reason` | string | yes | `判定理由` |
| `recommended_action` | string | yes | `推奨対応` |
| `span` | object | yes | File-format-specific location reference |

Validation:
- The same detected text in the same category receives the same replacement within a run.
- Sequence numbering is deterministic for the same inputs, settings, and applied languages.

## ProcessingReport

Represents `機密情報検出結果.xlsx`.

Required columns:
- `No`
- `検出語句`
- `置換提案`
- `原文または前後の文脈`
- `情報カテゴリ`
- `リスクレベル`
- `判定理由`
- `推奨対応`

Additional audit columns:
- `ファイルパス`
- `処理ステータス`
- `適用言語`
- `ルールID`
- `失敗またはスキップ理由`

Validation:
- Rows with `リスクレベル` are colored by risk level.
- Unsupported files appear with `処理ステータス = skipped_unsupported`.

## State Transitions

```text
discovered
  -> skipped_unsupported
  -> skipped_out_of_scope
  -> language_detected
  -> detection_completed
  -> no_replacement
  -> replacement_completed
  -> report_recorded
  -> failed
```

Failure transitions can occur from language detection, document loading, detection, replacement, or writing. Failures record a reason and preserve the original input.
