# Contract: `機密情報検出結果.xlsx`

## Required Sheet

The workbook must include a primary results sheet named `検出結果`.

## Required Columns

| Column | Source |
|--------|--------|
| `No` | Stable sequential report row number |
| `検出語句` | Detected text selected by the winning rule |
| `置換提案` | Deterministic `カテゴリ_連番` replacement |
| `原文または前後の文脈` | Text around the detection or status context |
| `情報カテゴリ` | Winning rule category |
| `リスクレベル` | Winning rule risk level |
| `判定理由` | Winning rule judgment reason |
| `推奨対応` | Winning rule recommended action |

## Audit Columns

| Column | Source |
|--------|--------|
| `ファイルパス` | Target file relative path |
| `処理ステータス` | Processing status |
| `適用言語` | Explicit or detected language |
| `ルールID` | Winning rule id, when applicable |
| `失敗またはスキップ理由` | Failure/skipped reason, when applicable |

## Row Coloring

| Risk Level | Row Color |
|------------|-----------|
| `high` | Light red |
| `medium` | Light yellow |
| `low` | Light green |
| No risk/status-only | Light gray |

## Required Report Rows

- One row per selected detection.
- One status-only row for each supported file with no replacements.
- One status-only row for each unsupported file with `処理ステータス = skipped_unsupported`.
- One status-only row for each out-of-scope or failed file with a reason.
