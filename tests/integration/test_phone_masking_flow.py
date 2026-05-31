from pathlib import Path

from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.core.processor import process


def _rule() -> MaskingRule:
    return MaskingRule("phone", "en", True, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0)


def test_phone_masking_flow_and_reproducible_rerun(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Call 202-555-0143 or 2025550143.", encoding="utf-8")

    out1, _ = process(make_file_selection(source, "en", tmp_path / "output"), [_rule()])
    out2, _ = process(make_file_selection(source, "en", tmp_path / "output"), [_rule()])

    assert (out1 / "files" / "sample.txt").read_text(encoding="utf-8") == "Call PHONE_001 or PHONE_002."
    assert (out2 / "files" / "sample.txt").read_text(encoding="utf-8") == "Call PHONE_001 or PHONE_002."


def test_repeated_identical_phone_value_reuses_replacement(tmp_path: Path) -> None:
    source = tmp_path / "repeated.txt"
    source.write_text("Call 202-555-0143, then call 202-555-0143 again.", encoding="utf-8")

    output_dir, results = process(make_file_selection(source, "en", tmp_path / "output"), [_rule()])

    assert (output_dir / "files" / "repeated.txt").read_text(encoding="utf-8") == (
        "Call PHONE_001, then call PHONE_001 again."
    )
    replacements = [detection.replacement for result in results for detection in result.detections]
    assert replacements == ["PHONE_001", "PHONE_001"]
