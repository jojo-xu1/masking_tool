from pathlib import Path
import hashlib

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.core.processor import process
from masking_tool.detection import person


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_input_hash_preserved(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    source = tmp_path / "sample.txt"
    source.write_text("Alice Smith", encoding="utf-8")
    before = _sha(source)
    process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))
    assert _sha(source) == before


def test_input_hash_preserved_for_phone_masking(tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")
    source = tmp_path / "phone.txt"
    source.write_text("Call 202-555-0143", encoding="utf-8")
    before = _sha(source)
    rules = [MaskingRule("phone", "en", True, RuleType.PHONE, "PHONE", RiskLevel.HIGH, "phone", "replace", 0)]

    process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert _sha(source) == before


def test_input_hash_preserved_for_person_masking(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pytest.importorskip("openpyxl")

    class _Entity:
        text = "Alice Johnson"
        start_char = 0
        end_char = 13
        label_ = "PERSON"

    class _Doc:
        ents = [_Entity()]

    monkeypatch.setattr(person, "load_spacy_model", lambda _: lambda text: _Doc())
    source = tmp_path / "person.txt"
    source.write_text("Alice Johnson", encoding="utf-8")
    before = _sha(source)
    rules = [
        MaskingRule("person", "en", True, RuleType.PERSON, "PERSON", RiskLevel.HIGH, "person", "replace", 0, model_name="model", required=True)
    ]

    process(make_file_selection(source, "en", tmp_path / "output"), rules)

    assert _sha(source) == before
