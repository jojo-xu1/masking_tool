from __future__ import annotations

import re

from masking_tool.core.models import MaskingRule, RuleType
from masking_tool.detection.matches import DetectionMatch


JP_POSTAL = re.compile(r"(?<!\d)\d{3}-\d{4}(?!\d)")
US_ZIP = re.compile(r"(?<![\d-])\d{5}(?:-\d{4})?(?![\d-])")
CN_POSTAL = re.compile(r"(?<!\d)\d{6}(?!\d)")
POSTAL_LABELS = {
    "en": re.compile(r"\b(?:postal\s+code|zip(?:\s+code)?|postcode)\b", re.IGNORECASE),
    "ja": re.compile(r"(?:郵便番号|〒)"),
    "zh": re.compile(r"(?:邮政编码|邮编|郵政編碼)"),
}
PHONE_LIKE = re.compile(r"(?:\+?\d[\d\s().-]{8,}\d)")
DATE_LIKE = re.compile(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b")
MONEY_OR_ACCOUNT_LABEL = re.compile(r"\b(?:amount|account|acct|invoice|社員番号|口座|金额|账号)\b", re.IGNORECASE)


def find_postal_matches(text: str, rules: list[MaskingRule]) -> list[DetectionMatch]:
    matches: list[DetectionMatch] = []
    for rule in rules:
        if not rule.enabled or rule.rule_type != RuleType.POSTAL_CODE:
            continue
        pattern = {"ja": JP_POSTAL, "en": US_ZIP, "zh": CN_POSTAL}.get(rule.language)
        if pattern is None:
            continue
        for match in pattern.finditer(text):
            value = match.group(0)
            if _is_false_positive(rule.language, text, match.start(), match.end(), value):
                continue
            matches.append(DetectionMatch(rule, match.start(), match.end(), value))
    return sorted(matches, key=lambda item: (item.start, item.end, item.rule.order))


def _is_false_positive(language: str, text: str, start: int, end: int, value: str) -> bool:
    line = _line_for(text, start, end)
    if PHONE_LIKE.fullmatch(line.strip()) or DATE_LIKE.search(line):
        return True
    if MONEY_OR_ACCOUNT_LABEL.search(line):
        return True
    if language == "en" and not (_has_label(language, line) or _looks_like_us_address_line(line)):
        return True
    if language == "ja" and not (_has_label(language, line) or "〒" in line or _looks_like_jp_address_line(line)):
        return True
    if language == "zh" and not (_has_label(language, line) or _looks_like_cn_address_line(line)):
        return True
    return False


def _line_for(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end < 0:
        line_end = len(text)
    return text[line_start:line_end]


def _has_label(language: str, line: str) -> bool:
    return bool(POSTAL_LABELS[language].search(line))


def _looks_like_us_address_line(line: str) -> bool:
    return bool(re.search(r"\b\d{1,6}\s+[A-Z][A-Za-z0-9 .'-]+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?)\b", line))


def _looks_like_jp_address_line(line: str) -> bool:
    return bool(re.search(r"(?:都|道|府|県).+(?:市|区|町|村).+\d", line))


def _looks_like_cn_address_line(line: str) -> bool:
    return bool(re.search(r"(?:省|市|自治区).+(?:区|县|路|街|号)", line))
