from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_files
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def _rules(language: str):
    return load_rule_files([f"src/masking_tool_defaults/{language}.yml"])


def test_japanese_address_and_postal_masking(tmp_path: Path) -> None:
    source = tmp_path / "ja.txt"
    source.write_text("〒100-0001 住所: 東京都千代田区千代田1-1\n", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "ja", tmp_path / "output"), _rules("ja"))

    masked = (output_dir / "files" / "ja.txt").read_text(encoding="utf-8")
    assert "POSTAL_CODE_001" in masked
    assert "ADDRESS_001" in masked
    assert "100-0001" not in masked
    assert "東京都千代田区千代田1-1" not in masked


def test_english_us_address_and_zip_masking(tmp_path: Path) -> None:
    source = tmp_path / "en.txt"
    source.write_text("ZIP: 10001 Address: 123 Market Street, New York, NY\n", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), _rules("en"))

    masked = (output_dir / "files" / "en.txt").read_text(encoding="utf-8")
    assert "POSTAL_CODE_001" in masked
    assert "ADDRESS_001" in masked
    assert "10001" not in masked
    assert "123 Market Street" not in masked


def test_chinese_address_and_postal_masking(tmp_path: Path) -> None:
    source = tmp_path / "zh.txt"
    source.write_text("邮政编码: 100000 地址: 北京市朝阳区建国路88号\n", encoding="utf-8")

    output_dir, _ = process(make_file_selection(source, "zh", tmp_path / "output"), _rules("zh"))

    masked = (output_dir / "files" / "zh.txt").read_text(encoding="utf-8")
    assert "POSTAL_CODE_001" in masked
    assert "ADDRESS_001" in masked
    assert "100000" not in masked
    assert "北京市朝阳区建国路88号" not in masked


def test_csv_header_postal_values_are_masked_for_each_language(tmp_path: Path) -> None:
    cases = [
        ("en", "name,zip,address\nAlice Smith,10001,\"123 Market Street, New York, NY\"\n", "10001"),
        ("ja", "name,郵便番号,address\n山田太郎,100-0001,東京都千代田区千代田1-1\n", "100-0001"),
        ("zh", "name,邮政编码,address\n张伟,100000,北京市朝阳区建国路88号\n", "100000"),
    ]

    for language, csv_text, original in cases:
        source = tmp_path / f"{language}.csv"
        source.write_text(csv_text, encoding="utf-8")

        output_dir, _ = process(make_file_selection(source, language, tmp_path / f"output-{language}"), _rules(language))

        masked = (output_dir / "files" / source.name).read_text(encoding="utf-8")
        assert "POSTAL_CODE_001" in masked
        assert original not in masked


def test_log_key_value_postal_values_are_masked_for_each_language(tmp_path: Path) -> None:
    cases = [
        ("en", "INFO postal=10001 owner=Alice Smith\n", "10001"),
        ("ja", "INFO postal=100-0001 owner=山田太郎\n", "100-0001"),
        ("zh", "INFO postal=100000 owner=张伟\n", "100000"),
    ]

    for language, log_text, original in cases:
        source = tmp_path / f"{language}.log"
        source.write_text(log_text, encoding="utf-8")

        output_dir, _ = process(make_file_selection(source, language, tmp_path / f"log-output-{language}"), _rules(language))

        masked = (output_dir / "files" / source.name).read_text(encoding="utf-8")
        assert "POSTAL_CODE_001" in masked
        assert original not in masked


def test_xlsx_left_label_postal_values_are_masked(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "postal.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["field", "value"])
    sheet.append(["postal", "10001"])
    workbook.save(source)

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "xlsx-output"), _rules("en"))

    workbook = openpyxl.load_workbook(output_dir / "files" / "postal.xlsx")
    assert workbook.active["B2"].value == "POSTAL_CODE_001"
