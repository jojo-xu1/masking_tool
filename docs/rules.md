# Rule Maintenance

Default rules live in `src/masking_tool_defaults/`.

Each rule file declares:
- `language`: `en`, `ja`, or `zh`
- `version`: positive integer
- `rules`: ordered list of regex or explicit rules

Conflict priority:
1. Explicit rules
2. Higher risk level
3. Earlier configuration order

Replacement suggestions are generated as `CATEGORY_001`, `CATEGORY_002`, and so
on for each category.
