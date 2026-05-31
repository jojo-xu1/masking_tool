from pathlib import Path

from masking_tool.config.loader import load_rule_file


def test_disabled_rule_is_loaded_as_disabled(tmp_path: Path) -> None:
    config = tmp_path / "rules.yml"
    config.write_text(
        """
language: en
version: 1
rules:
  - id: off
    enabled: false
    type: explicit
    category: TEST
    risk_level: low
    literal: secret
    judgment_reason: test
    recommended_action: test
""",
        encoding="utf-8",
    )
    assert load_rule_file(config)[0].enabled is False
