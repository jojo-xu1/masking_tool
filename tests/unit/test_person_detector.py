from pathlib import Path

import pytest

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType, TargetFile
from masking_tool.detection import person
from masking_tool.detection.person import PersonDetectionUnavailable, find_person_matches


class _Entity:
    def __init__(self, text: str, start: int, end: int, label: str = "PERSON") -> None:
        self.text = text
        self.start_char = start
        self.end_char = end
        self.label_ = label


class _Doc:
    def __init__(self, ents: list[_Entity]) -> None:
        self.ents = ents


def _rule(language: str, required: bool, behavior: str = "fail") -> MaskingRule:
    return MaskingRule(
        f"{language}-person",
        language,
        True,
        RuleType.PERSON,
        "PERSON",
        RiskLevel.HIGH,
        "Detected as person",
        "Replace",
        0,
        model_name=f"{language}_model",
        required=required,
        unavailable_behavior=behavior,
    )


def _target(language: str) -> TargetFile:
    return TargetFile(Path("sample.txt"), Path("sample.txt"), ".txt", "eligible", applied_language=language)


def test_person_detector_returns_person_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc([_Entity("Alice", 0, 5)]))

    matches = find_person_matches(_target("en"), "Alice joined", [_rule("en", True)])

    assert matches[0].text == "Alice"
    assert matches[0].rule.category == "PERSON"


def test_required_person_model_failure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_: str) -> object:
        raise PersonDetectionUnavailable("missing model")

    monkeypatch.setattr(person, "load_spacy_model", _raise)

    with pytest.raises(PersonDetectionUnavailable, match="missing model"):
        find_person_matches(_target("ja"), "山田太郎", [_rule("ja", True)])


def test_optional_chinese_model_failure_uses_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_: str) -> object:
        raise PersonDetectionUnavailable("missing zh model")

    target = _target("zh")
    monkeypatch.setattr(person, "load_spacy_model", _raise)

    matches = find_person_matches(target, "负责人: 张伟。张伟批准了草案。", [_rule("zh", False, "fallback_heuristic")])

    assert [match.text for match in matches] == ["张伟", "张伟"]
    assert target.failure_reason is None


def test_chinese_fallback_ignores_non_person_terms(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_: str) -> object:
        raise PersonDetectionUnavailable("missing zh model")

    monkeypatch.setattr(person, "load_spacy_model", _raise)

    assert find_person_matches(_target("zh"), "联系电话是+86 10 1234 5678。秘密项目需要确认。", [_rule("zh", False, "fallback_heuristic")]) == []


def test_japanese_person_detector_supplements_log_and_csv_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc([]))

    text = "owner=山田太郎 phone=03-1234-5678\nname,email\n佐藤花子,hanako@example.jp"
    matches = find_person_matches(_target("ja"), text, [_rule("ja", True)])

    assert [match.text for match in matches] == ["山田太郎", "佐藤花子"]


def test_language_filter_ignores_ascii_entities_for_japanese(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc([_Entity("owner", 0, 5)]))

    matches = find_person_matches(_target("ja"), "owner=山田太郎", [_rule("ja", True)])

    assert [match.text for match in matches] == ["山田太郎"]
