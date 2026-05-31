# Rule Maintenance

Default rules live in `src/masking_tool_defaults/`.

Each rule file declares:
- `language`: `en`, `ja`, or `zh`
- `version`: positive integer
- `rules`: ordered list of regex or explicit rules
- `sources`: ordered list of configurable detection sources such as person,
  phone, address, and postal-code detection

Conflict priority:
1. Explicit rules
2. Higher risk level
3. Earlier configuration order

Replacement suggestions are generated as `CATEGORY_001`, `CATEGORY_002`, and so
on for each category.

## Default Detection Sources

Address and postal-code sources are enabled by default in `en.yml`, `ja.yml`,
and `zh.yml`.

- `en`: representative US street addresses and ZIP codes such as `10001`
- `ja`: representative Japan addresses and postal codes such as `100-0001`
- `zh`: representative China addresses and postal codes such as `100000`

Address detection is intentionally narrow. It accepts address labels such as
`Address:`, `住所:`, and `地址:` or clear country-specific structures. Ambiguous
location-like notes are not masked as addresses by default. Postal-code detection
filters obvious dates, phone numbers, account-like values, money/account labels,
and country formats outside the applied language scope.

Postal-code context can come from inline labels such as `Postal code:`, `ZIP:`,
`postal=`, `郵便番号=`, and `邮编=`, from CSV column headers such as `postal`,
`zip`, `郵便番号`, or `邮政编码`, and from XLSX left-neighbor or header cells that
label the adjacent value as a postal code.
