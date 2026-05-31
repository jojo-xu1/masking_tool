from pathlib import Path

import pytest

from masking_tool.config.loader import load_rule_file
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.processor import process


def test_office_document_uses_pre_replacement_line_context(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "office.docx"
    document = docx.Document()
    line = "Contact Alice Smith at alice@example.com"
    document.add_paragraph(line)
    document.save(source)

    output_dir, results = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))

    assert len(results[0].detections) == 2
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    assert all(line in row[3] for row in rows[1:] if row[4] != "STATUS")


def test_text_pdf_uses_pre_replacement_line_context(tmp_path: Path) -> None:
    fitz = pytest.importorskip("fitz")
    openpyxl = pytest.importorskip("openpyxl")
    source = tmp_path / "report.pdf"
    document = fitz.open()
    page = document.new_page()
    line = "Contact Alice Smith at alice@example.com"
    page.insert_text((72, 72), line)
    document.save(source)

    output_dir, results = process(make_file_selection(source, "en", tmp_path / "output"), load_rule_file("tests/fixtures/rules/test_rules.yml"))

    assert len(results[0].detections) == 2
    rows = list(openpyxl.load_workbook(output_dir / "機密情報検出結果.xlsx")["検出結果"].iter_rows(values_only=True))
    assert all(line in row[3] for row in rows[1:] if row[4] != "STATUS")
