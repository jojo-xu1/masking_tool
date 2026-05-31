from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.phone import find_phone_matches


def _rule() -> MaskingRule:
    return MaskingRule("phone", "en", True, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0)


def test_phone_detector_matches_japanese_us_and_chinese_formats() -> None:
    text = "JP 03-1234-5678, US +1-202-555-0143, CN +86 10 1234 5678, mobile 13800138000"

    values = [match.text for match in find_phone_matches(text, [_rule()])]

    assert "03-1234-5678" in values
    assert "+1-202-555-0143" in values
    assert "+86 10 1234 5678" in values
    assert "13800138000" in values


def test_phone_detector_matches_numbers_adjacent_to_cjk_text() -> None:
    text = "電話番号は03-1234-5678です。联系电话是+86 10 1234 5678。"

    values = [match.text for match in find_phone_matches(text, [_rule()])]

    assert "03-1234-5678" in values
    assert "+86 10 1234 5678" in values
    assert "10 1234 5678" not in values
