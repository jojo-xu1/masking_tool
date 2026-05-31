from pathlib import Path

import pytest

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType, TargetFile
from masking_tool.detection import person
from masking_tool.detection.detector import detect_text
from masking_tool.replacement.mapping import ReplacementMapper


class _Entity:
    text = "Alice Johnson"
    start_char = 0
    end_char = 13
    label_ = "PERSON"


class _Doc:
    ents = [_Entity()]


def test_person_detection_contract_reports_person(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc())
    target = TargetFile(Path("sample.txt"), Path("sample.txt"), ".txt", "eligible", applied_language="en")
    rule = MaskingRule("person", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "Detected as person", "Replace", 0, model_name="model", required=True)

    detections = detect_text(target, "Alice Johnson", [rule], ReplacementMapper())

    assert detections[0].detected_text == "Alice Johnson"
    assert detections[0].replacement == "PERSON_001"
    assert detections[0].category == "PERSON"
