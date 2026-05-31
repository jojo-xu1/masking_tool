from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.phone import find_phone_matches


def test_phone_detector_ignores_negative_numeric_examples() -> None:
    rule = MaskingRule("phone", "en", True, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0)
    text = "2026-05-30 100-0001 90210 12345 12345678901234567890"

    assert find_phone_matches(text, [rule]) == []
