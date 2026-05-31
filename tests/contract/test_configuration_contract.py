from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file


def test_configuration_contract_loads_required_fields() -> None:
    rules = load_rule_file(Path("tests/fixtures/rules/test_rules.yml"))
    assert [rule.id for rule in rules] == ["en-email", "en-name"]
    assert rules[0].category == "EMAIL"
    assert rules[0].enabled is True


def test_configuration_contract_rejects_missing_pattern(tmp_path: Path) -> None:
    config = tmp_path / "bad.yml"
    config.write_text(
        """
language: en
version: 1
rules:
  - id: bad
    enabled: true
    type: regex
    category: EMAIL
    risk_level: high
    judgment_reason: bad
    recommended_action: bad
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_rule_file(config)
