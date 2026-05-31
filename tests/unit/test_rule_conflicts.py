from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.rules import find_rule_matches, resolve_conflicts


def _rule(rule_id: str, rule_type: RuleType, risk: RiskLevel, order: int, pattern: str | None = None, literal: str | None = None) -> MaskingRule:
    return MaskingRule(rule_id, "en", True, rule_type, "X", risk, "reason", "action", order, pattern, literal)


def test_explicit_rule_wins_over_regex() -> None:
    rules = [
        _rule("regex", RuleType.REGEX, RiskLevel.HIGH, 0, pattern="Alice Smith"),
        _rule("explicit", RuleType.EXPLICIT, RiskLevel.LOW, 1, literal="Alice Smith"),
    ]
    winners = resolve_conflicts(find_rule_matches("Alice Smith", rules))
    assert [winner.rule.id for winner in winners] == ["explicit"]


def test_higher_risk_then_order_wins() -> None:
    rules = [
        _rule("low", RuleType.REGEX, RiskLevel.LOW, 0, pattern="Alice"),
        _rule("high", RuleType.REGEX, RiskLevel.HIGH, 1, pattern="Alice"),
    ]
    winners = resolve_conflicts(find_rule_matches("Alice", rules))
    assert [winner.rule.id for winner in winners] == ["high"]
