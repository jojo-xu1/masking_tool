# Report Contract

## Workbook

- File name: `機密情報検出結果.xlsx`
- Sheet name: `検出結果`
- Header row: frozen
- Filters: enabled for all required columns
- Long text cells: wrapped
- Row colors: based on risk level or status-only row state

## Required Columns

The report must contain exactly these columns in this order:

1. `No`
2. `検出語句`
3. `置換提案`
4. `原文または前後の文脈`
5. `情報カテゴリ`
6. `リスクレベル`
7. `判定理由`
8. `推奨対応`

No audit-only columns may be appended.

## Detection Row

Detection rows must populate:

- `No`: deterministic row number
- `検出語句`: original detected value
- `置換提案`: deterministic replacement value
- `原文または前後の文脈`: surrounding context and target-file clue when needed
- `情報カテゴリ`: category such as `PERSON`, `PHONE`, or existing configured category
- `リスクレベル`: `high`, `medium`, or `low`
- `判定理由`: rule or detection-source reason
- `推奨対応`: recommended masking action

## Status-Only Row

Rows for unsupported, out-of-scope, no-replacement, and failed files must stay within the same 8 columns:

- `検出語句`: empty
- `置換提案`: empty
- `原文または前後の文脈`: target-file clue and status summary
- `情報カテゴリ`: status category or empty
- `リスクレベル`: empty or status-neutral value
- `判定理由`: skip/failure/status reason
- `推奨対応`: next action when applicable

## Formatting Requirements

- Header row must remain visible while scrolling.
- Column filters must allow category and risk filtering.
- Context, reason, and action columns must be readable without manual resizing.
- Risk-level row coloring must continue to distinguish high, medium, and low.
- Status-only rows must be visually distinguishable without adding columns.
