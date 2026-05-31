from pathlib import Path

from masking_tool.config.loader import load_rule_files
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_repeated_address_and_postal_values_reuse_deterministic_replacements(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text(
        "Postal code: 10001 Address: 123 Market Street, New York, NY\n"
        "Postal code: 10001 Address: 123 Market Street, New York, NY\n",
        encoding="utf-8",
    )

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_files(["src/masking_tool_defaults/en.yml"]))

    masked = (output_dir / "files" / "sample.txt").read_text(encoding="utf-8")
    assert masked.count("POSTAL_CODE_001") == 2
    assert masked.count("ADDRESS_001") == 2
    assert "POSTAL_CODE_002" not in masked
    assert "ADDRESS_002" not in masked
