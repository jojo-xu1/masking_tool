from pathlib import Path

from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.core.processor import process


def test_disabled_phone_detection_preserves_other_rules(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Call 202-555-0143 and email alice@example.com", encoding="utf-8")
    rules = [
        MaskingRule("phone", "en", False, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0),
        MaskingRule("email", "en", True, RuleType.REGEX, "EMAIL", RiskLevel.HIGH, "email", "replace", 1, pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ]

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert (output_dir / "files" / "sample.txt").read_text(encoding="utf-8") == "Call 202-555-0143 and email EMAIL_001"
