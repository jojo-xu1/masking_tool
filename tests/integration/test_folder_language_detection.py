from masking_tool.detection.language import detect_language


def test_folder_language_detection() -> None:
    assert detect_language("hello world")[0] == "en"
    assert detect_language("これは日本語です")[0] == "ja"
    assert detect_language("秘密项目")[0] == "zh"
