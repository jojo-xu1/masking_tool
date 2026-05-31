from masking_tool.config.loader import load_rule_files


def test_default_language_rules_load() -> None:
    rules = load_rule_files([
        "src/masking_tool_defaults/en.yml",
        "src/masking_tool_defaults/ja.yml",
        "src/masking_tool_defaults/zh.yml",
    ])
    assert {"en", "ja", "zh"} <= {rule.language for rule in rules}
