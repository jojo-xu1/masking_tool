from masking_tool.config.loader import load_rule_file
from masking_tool.detection.rules import find_rule_matches


def test_regex_rule_matches_email() -> None:
    rules = load_rule_file("tests/fixtures/rules/test_rules.yml")
    matches = find_rule_matches("alice@example.com", rules)
    assert any(match.rule.id == "en-email" for match in matches)
