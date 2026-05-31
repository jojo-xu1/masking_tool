# Contract: Rule Configuration

Rule configuration is loaded from default language files and optional user-provided files. Defaults must exist for English, Japanese, and Chinese.

## File Shape

```yaml
language: ja
version: 1
rules:
  - id: ja-email
    enabled: true
    type: regex
    category: EMAIL
    risk_level: high
    pattern: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
    judgment_reason: "メールアドレス形式に一致"
    recommended_action: "外部共有前に置換"
  - id: ja-project-code
    enabled: true
    type: explicit
    category: PROJECT
    risk_level: medium
    literal: "Project Sakura"
    judgment_reason: "個別指定された機密語句"
    recommended_action: "公開資料では置換"
```

## Required Fields

| Field | Requirement |
|-------|-------------|
| `language` | One of `en`, `ja`, `zh` |
| `version` | Positive integer |
| `rules[].id` | Unique across loaded rule files |
| `rules[].enabled` | Boolean |
| `rules[].type` | `regex` or `explicit` |
| `rules[].category` | Non-empty uppercase label used in `カテゴリ_連番` |
| `rules[].risk_level` | `high`, `medium`, or `low` |
| `rules[].pattern` | Required when `type = regex` |
| `rules[].literal` | Required when `type = explicit` |
| `rules[].judgment_reason` | Non-empty report value |
| `rules[].recommended_action` | Non-empty report value |

## Conflict Rules

When multiple enabled rules match the same text span:

1. Explicit rules beat regex rules.
2. Higher risk beats lower risk.
3. Earlier configuration order wins remaining ties.

## Validation Errors

Configuration loading fails before file processing when:
- Any required default language file is missing.
- A rule id is duplicated.
- A regex pattern cannot compile.
- A required field is missing.
- A rule declares an unsupported language or risk level.
