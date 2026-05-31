from pathlib import Path

import pytest

from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.core.processor import process
from masking_tool.detection import person


class _Entity:
    def __init__(self, text: str, start: int, end: int) -> None:
        self.text = text
        self.start_char = start
        self.end_char = end
        self.label_ = "PERSON"


def test_person_masking_flow_masks_english_and_japanese(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _model(_: str):
        def _detect(text: str):
            if "Alice Johnson" in text:
                return type("Doc", (), {"ents": [_Entity("Alice Johnson", text.index("Alice Johnson"), text.index("Alice Johnson") + 13)]})()
            return type("Doc", (), {"ents": [_Entity("山田太郎", text.index("山田太郎"), text.index("山田太郎") + 4)]})()

        return _detect

    monkeypatch.setattr(person, "load_spacy_model", _model)
    rules = [
        MaskingRule("en-person", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="en_model", required=True),
        MaskingRule("ja-person", "ja", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="ja_model", required=True),
    ]

    en_source = tmp_path / "en.txt"
    en_source.write_text("Alice Johnson signed.", encoding="utf-8")
    en_output, _ = process(make_file_selection(en_source, "en", tmp_path / "output"), rules)
    assert (en_output / "files" / "en.txt").read_text(encoding="utf-8") == "PERSON_001 signed."

    ja_source = tmp_path / "ja.txt"
    ja_source.write_text("山田太郎が署名しました。", encoding="utf-8")
    ja_output, _ = process(make_file_selection(ja_source, "ja", tmp_path / "output"), rules)
    assert (ja_output / "files" / "ja.txt").read_text(encoding="utf-8") == "PERSON_001が署名しました。"


def test_person_masking_flow_masks_repeated_same_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _model(_: str):
        def _detect(text: str):
            start = text.index("Alice Johnson")
            return type("Doc", (), {"ents": [_Entity("Alice Johnson", start, start + 13)]})()

        return _detect

    monkeypatch.setattr(person, "load_spacy_model", _model)
    rules = [
        MaskingRule("en-person", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="en_model", required=True),
    ]
    source = tmp_path / "repeated-person.txt"
    source.write_text("Alice Johnson approved it. Alice Johnson signed it.", encoding="utf-8")

    output_dir, results = process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert (output_dir / "files" / "repeated-person.txt").read_text(encoding="utf-8") == (
        "PERSON_001 approved it. PERSON_001 signed it."
    )
    replacements = [detection.replacement for result in results for detection in result.detections]
    assert replacements == ["PERSON_001", "PERSON_001"]


def test_person_repeat_expansion_does_not_mask_inside_words(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _model(_: str):
        def _detect(text: str):
            start = text.index("Ann")
            return type("Doc", (), {"ents": [_Entity("Ann", start, start + 3)]})()

        return _detect

    monkeypatch.setattr(person, "load_spacy_model", _model)
    rules = [
        MaskingRule("en-person", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="en_model", required=True),
    ]
    source = tmp_path / "person-boundary.txt"
    source.write_text("Ann met Annual Review.", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert (output_dir / "files" / "person-boundary.txt").read_text(encoding="utf-8") == "PERSON_001 met Annual Review."


def test_chinese_person_masking_uses_fallback_when_spacy_model_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(_: str) -> object:
        raise person.PersonDetectionUnavailable("missing zh model")

    monkeypatch.setattr(person, "load_spacy_model", _raise)
    rules = [
        MaskingRule(
            "zh-person",
            "zh",
            True,
            RuleType.PERSON,
            "PERSON",
            RiskLevel.HIGH,
            "person",
            "replace",
            0,
            model_name="zh_model",
            unavailable_behavior="fallback_heuristic",
        ),
    ]
    source = tmp_path / "zh.txt"
    source.write_text("负责人: 张伟。张伟批准了草案。", encoding="utf-8")

    output_dir, results = process(make_file_selection(source, "zh", tmp_path / "output"), rules)

    assert (output_dir / "files" / "zh.txt").read_text(encoding="utf-8") == "负责人: PERSON_001。PERSON_001批准了草案。"
    replacements = [detection.replacement for result in results for detection in result.detections]
    assert replacements == ["PERSON_001", "PERSON_001"]
