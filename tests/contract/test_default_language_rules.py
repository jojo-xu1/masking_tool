from masking_tool.config.loader import load_rule_files


DEFAULT_RULE_PATHS = [
    "src/masking_tool_defaults/en.yml",
    "src/masking_tool_defaults/ja.yml",
    "src/masking_tool_defaults/zh.yml",
]


def test_default_language_rules_load() -> None:
    rules = load_rule_files(DEFAULT_RULE_PATHS)

    assert {"en", "ja", "zh"} <= {rule.language for rule in rules}


def test_address_and_postal_default_sources_are_configurable() -> None:
    rules = load_rule_files(DEFAULT_RULE_PATHS)
    by_id = {rule.id: rule for rule in rules}

    for language in ("en", "ja", "zh"):
        assert by_id[f"{language}-address"].enabled
        assert by_id[f"{language}-address"].rule_type.value == "address"
        assert by_id[f"{language}-address"].category == "ADDRESS"
        assert by_id[f"{language}-postal-code"].enabled
        assert by_id[f"{language}-postal-code"].rule_type.value == "postal_code"
        assert by_id[f"{language}-postal-code"].category == "POSTAL_CODE"
