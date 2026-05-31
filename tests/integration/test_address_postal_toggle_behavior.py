from dataclasses import replace
from pathlib import Path

from masking_tool.config.loader import load_rule_files
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_disabling_address_and_postal_sources_preserves_person_and_phone_masking(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text(
        "Owner: Alice Smith Phone: 202-555-0143 Postal code: 10001 Address: 123 Market Street, New York, NY\n",
        encoding="utf-8",
    )
    rules = [
        replace(rule, enabled=False) if rule.rule_type.value in {"address", "postal_code"} else rule
        for rule in load_rule_files(["src/masking_tool_defaults/en.yml"])
    ]

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), rules)

    masked = (output_dir / "files" / "sample.txt").read_text(encoding="utf-8")
    assert "PERSON_" in masked
    assert "PHONE_" in masked
    assert "10001" in masked
    assert "123 Market Street" in masked
