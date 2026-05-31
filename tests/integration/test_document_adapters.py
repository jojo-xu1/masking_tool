from pathlib import Path

import pytest

from masking_tool.formats.text_adapter import read_text_file, write_text_file


def test_text_adapter_smoke(tmp_path: Path) -> None:
    path = tmp_path / "a.log"
    write_text_file(path, "hello")
    assert read_text_file(path) == "hello"


def test_xlsx_adapter_smoke(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    from masking_tool.formats.xlsx_adapter import read_xlsx_text, write_xlsx_text

    source = tmp_path / "a.xlsx"
    workbook = openpyxl.Workbook()
    workbook.active["A1"] = "secret"
    workbook.save(source)
    assert read_xlsx_text(source) == "secret"
    output = tmp_path / "out.xlsx"
    write_xlsx_text(source, output, "masked")
    assert read_xlsx_text(output) == "masked"


def test_docx_adapter_smoke(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    from masking_tool.formats.docx_adapter import read_docx_text, write_docx_text

    source = tmp_path / "a.docx"
    document = docx.Document()
    document.add_paragraph("secret")
    document.save(source)
    assert read_docx_text(source) == "secret"
    output = tmp_path / "out.docx"
    write_docx_text(source, output, "masked")
    assert read_docx_text(output) == "masked"


def test_pptx_adapter_smoke(tmp_path: Path) -> None:
    pptx = pytest.importorskip("pptx")
    from masking_tool.formats.pptx_adapter import read_pptx_text, write_pptx_text

    source = tmp_path / "a.pptx"
    presentation = pptx.Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[5])
    shape = slide.shapes.add_textbox(0, 0, 100, 100)
    shape.text = "secret"
    presentation.save(source)
    assert "secret" in read_pptx_text(source)
    output = tmp_path / "out.pptx"
    write_pptx_text(source, output, "masked")
    assert "masked" in read_pptx_text(output)


def test_pdf_adapter_out_of_scope_empty_pdf(tmp_path: Path) -> None:
    fitz = pytest.importorskip("fitz")
    from masking_tool.formats.pdf_adapter import read_pdf_text

    source = tmp_path / "empty.pdf"
    document = fitz.open()
    document.new_page()
    document.save(source)
    with pytest.raises(RuntimeError, match="no extractable text"):
        read_pdf_text(source)
