from pathlib import Path

from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.core.processor import process


def test_disabled_person_detection_preserves_regex_rules(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Alice Johnson alice@example.com", encoding="utf-8")
    rules = [
        MaskingRule("person", "en", False, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="missing", required=True),
        MaskingRule("email", "en", True, RuleType.REGEX, "EMAIL", RiskLevel.HIGH, "email", "replace", 1, pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ]

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert (output_dir / "files" / "sample.txt").read_text(encoding="utf-8") == "Alice Johnson EMAIL_001"
