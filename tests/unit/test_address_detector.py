from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.address import find_address_matches


def _rule(language: str) -> MaskingRule:
    return MaskingRule(f"{language}-address", language, True, RuleType.ADDRESS, "ADDRESS", RiskLevel.HIGH, "reason", "action", 1)


def test_labeled_and_structurally_clear_addresses_are_detected() -> None:
    cases = [
        ("en", "Address: 123 Market Street, New York, NY", "123 Market Street, New York, NY"),
        ("ja", "住所: 東京都千代田区千代田1-1", "東京都千代田区千代田1-1"),
        ("zh", "地址: 北京市朝阳区建国路88号", "北京市朝阳区建国路88号"),
    ]

    for language, text, expected in cases:
        assert [match.text for match in find_address_matches(text, [_rule(language)])] == [expected]


def test_ambiguous_unlabeled_location_text_is_not_address_masked() -> None:
    cases = [
        ("en", "Meeting in New York office"),
        ("ja", "東京オフィスで会議"),
        ("zh", "北京办公室会议"),
    ]

    for language, text in cases:
        assert find_address_matches(text, [_rule(language)]) == []
