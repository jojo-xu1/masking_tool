from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.address import find_address_matches
from masking_tool.detection.postal import find_postal_matches


def _rule(rule_type: RuleType, category: str) -> MaskingRule:
    return MaskingRule(category.lower(), "ja", True, rule_type, category, RiskLevel.HIGH, "reason", "action", 1)


def test_adjacent_japanese_postal_code_and_address_have_non_overlapping_spans() -> None:
    text = "〒100-0001 住所: 東京都千代田区千代田1-1"
    postal = find_postal_matches(text, [_rule(RuleType.POSTAL_CODE, "POSTAL_CODE")])[0]
    address = find_address_matches(text, [_rule(RuleType.ADDRESS, "ADDRESS")])[0]

    assert postal.text == "100-0001"
    assert address.text == "東京都千代田区千代田1-1"
    assert postal.end <= address.start
