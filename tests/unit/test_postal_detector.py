from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.postal import find_postal_matches


def _rule(language: str) -> MaskingRule:
    return MaskingRule(f"{language}-postal", language, True, RuleType.POSTAL_CODE, "POSTAL_CODE", RiskLevel.MEDIUM, "reason", "action", 1)


def test_japanese_postal_positive_and_negative_examples() -> None:
    text = "郵便番号: 100-0001\n確認日: 2026-05-31\n電話: 03-1234-5678\n米国ZIP: 10001"

    assert [match.text for match in find_postal_matches(text, [_rule("ja")])] == ["100-0001"]


def test_us_zip_positive_and_negative_examples() -> None:
    text = "Postal code: 10001\nAddress: 123 Market Street, New York, NY 10001\nDate: 2026-05-31\nJapan: 100-0001"

    assert [match.text for match in find_postal_matches(text, [_rule("en")])] == ["10001", "10001"]


def test_china_postal_positive_and_negative_examples() -> None:
    text = "邮政编码: 100000\n账号: 123456\n日期: 2026-05-31\n美国ZIP: 10001"

    assert [match.text for match in find_postal_matches(text, [_rule("zh")])] == ["100000"]


def test_equals_style_postal_labels_are_detected_by_language() -> None:
    cases = [
        ("en", "postal=10001\nzip=10002", ["10001", "10002"]),
        ("ja", "postal=100-0001\n郵便番号=150-0001", ["100-0001", "150-0001"]),
        ("zh", "postal=100000\n邮编=200000", ["100000", "200000"]),
    ]

    for language, text, expected in cases:
        assert [match.text for match in find_postal_matches(text, [_rule(language)])] == expected


def test_csv_header_context_detects_postal_values_without_inline_label() -> None:
    cases = [
        ("en", "name,zip,note\nAlice Smith,10001,office", ["10001"]),
        ("ja", "name,郵便番号,note\n山田太郎,100-0001,本社", ["100-0001"]),
        ("zh", "name,邮政编码,note\n张伟,100000,总部", ["100000"]),
    ]

    for language, text, expected in cases:
        assert [match.text for match in find_postal_matches(text, [_rule(language)])] == expected
