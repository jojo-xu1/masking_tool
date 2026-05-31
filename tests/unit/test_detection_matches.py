from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.matches import DetectionMatch, resolve_overlaps


def _rule(rule_id: str, rule_type: RuleType, risk: RiskLevel, order: int) -> MaskingRule:
    return MaskingRule(rule_id, "en", True, rule_type, "X", risk, "reason", "action", order)


def test_normalized_match_exposes_source_and_category() -> None:
    rule = _rule("en-phone", RuleType.PHONE, RiskLevel.HIGH, 2)
    match = DetectionMatch(rule, 4, 14, "2025550143")

    assert match.source_id == "en-phone"
    assert match.category == "X"


def test_explicit_then_risk_then_order_resolves_overlaps() -> None:
    low_explicit = DetectionMatch(_rule("explicit", RuleType.EXPLICIT, RiskLevel.LOW, 10), 0, 5, "Alice")
    high_regex = DetectionMatch(_rule("regex", RuleType.REGEX, RiskLevel.HIGH, 0), 0, 5, "Alice")
    high_phone = DetectionMatch(_rule("phone", RuleType.PHONE, RiskLevel.HIGH, 1), 10, 20, "2025550143")
    low_phone = DetectionMatch(_rule("low-phone", RuleType.PHONE, RiskLevel.LOW, 0), 10, 20, "2025550143")

    winners = resolve_overlaps([high_regex, low_explicit, low_phone, high_phone])

    assert [winner.rule.id for winner in winners] == ["explicit", "phone"]
