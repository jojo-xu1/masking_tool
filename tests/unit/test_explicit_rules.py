from masking_tool.config.loader import load_rule_file
from masking_tool.detection.rules import find_rule_matches


def test_explicit_rule_matches_literal() -> None:
    rules = load_rule_file("tests/fixtures/rules/test_rules.yml")
    matches = find_rule_matches("Alice Smith", rules)
    assert any(match.rule.id == "en-name" for match in matches)
