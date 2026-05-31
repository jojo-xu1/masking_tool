from pathlib import Path

import pytest


SAMPLE_ROOT = Path("docs/test-files/by-language")
EXPECTED_BY_LANGUAGE = {
    "en": {
        "text": ["en_sample.txt", "en_contacts.csv", "en_app.log"],
        "office": ["en_office.docx", "en_workbook.xlsx", "en_presentation.pptx"],
        "pdf": "en_text_pdf.pdf",
        "unsupported": "unsupported_en.md",
        "needles": ["Alice Smith", "202-555-0143"],
    },
    "ja": {
        "text": ["ja_sample.txt", "ja_contacts.csv", "ja_app.log"],
        "office": ["ja_office.docx", "ja_workbook.xlsx", "ja_presentation.pptx"],
        "pdf": "ja_text_pdf.pdf",
        "unsupported": "unsupported_ja.md",
        "needles": ["山田太郎", "03-1234-5678"],
    },
    "zh": {
        "text": ["zh_sample.txt", "zh_contacts.csv", "zh_app.log"],
        "office": ["zh_office.docx", "zh_workbook.xlsx", "zh_presentation.pptx"],
        "pdf": "zh_text_pdf.pdf",
        "unsupported": "unsupported_zh.md",
        "needles": ["张伟", "13800138000"],
    },
}


def test_language_separated_sample_inventory() -> None:
    for language, expected in EXPECTED_BY_LANGUAGE.items():
        folder = SAMPLE_ROOT / language
        assert folder.is_dir()
        for filename in [*expected["text"], *expected["office"], expected["pdf"], expected["unsupported"]]:
            assert (folder / filename).is_file()


def test_japanese_and_chinese_office_and_pdf_samples_keep_readable_cjk_text() -> None:
    pytest.importorskip("docx")
    pytest.importorskip("openpyxl")
    pytest.importorskip("pptx")
    pytest.importorskip("fitz")

    from masking_tool.formats.docx_adapter import read_docx_text
    from masking_tool.formats.pdf_adapter import read_pdf_text
    from masking_tool.formats.pptx_adapter import read_pptx_text
    from masking_tool.formats.xlsx_adapter import read_xlsx_text

    readers = {
        ".docx": read_docx_text,
        ".xlsx": read_xlsx_text,
        ".pptx": read_pptx_text,
        ".pdf": read_pdf_text,
    }
    for language in ("ja", "zh"):
        folder = SAMPLE_ROOT / language
        expected = EXPECTED_BY_LANGUAGE[language]
        for filename in [*expected["office"], expected["pdf"]]:
            text = readers[Path(filename).suffix](folder / filename)
            for needle in expected["needles"]:
                assert needle in text
