from pathlib import Path

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
