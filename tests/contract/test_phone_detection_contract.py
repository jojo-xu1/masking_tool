from pathlib import Path

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType, TargetFile
from masking_tool.detection.detector import detect_text
from masking_tool.replacement.mapping import ReplacementMapper


def test_phone_detection_contract_reports_phone() -> None:
    target = TargetFile(Path("sample.txt"), Path("sample.txt"), ".txt", "eligible", applied_language="en")
    rule = MaskingRule("phone", "en", True, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0)

    detections = detect_text(target, "Call 202-555-0143 today", [rule], ReplacementMapper())

    assert detections[0].detected_text == "202-555-0143"
    assert detections[0].replacement == "PHONE_001"
    assert detections[0].category == "PHONE"
