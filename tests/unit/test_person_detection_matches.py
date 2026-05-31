from pathlib import Path

import pytest

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType, TargetFile
from masking_tool.detection import person
from masking_tool.detection.person import find_person_matches
from masking_tool.replacement.mapping import ReplacementMapper


class _Entity:
    text = "Alice Johnson"
    start_char = 0
    end_char = 13
    label_ = "PERSON"


class _Doc:
    ents = [_Entity()]


def test_person_match_uses_deterministic_replacement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc())
    rule = MaskingRule("en-person-spacy", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "reason", "action", 0, model_name="model", required=True)
    target = TargetFile(Path("sample.txt"), Path("sample.txt"), ".txt", "eligible", applied_language="en")
    match = find_person_matches(target, "Alice Johnson", [rule])[0]
    mapper = ReplacementMapper()

    assert mapper.get(match.rule.category, match.text) == "PERSON_001"
    assert mapper.get(match.rule.category, match.text) == "PERSON_001"
