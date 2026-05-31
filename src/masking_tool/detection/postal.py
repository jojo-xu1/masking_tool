from __future__ import annotations

import re
from csv import reader

from masking_tool.core.models import MaskingRule, RuleType
from masking_tool.detection.matches import DetectionMatch


JP_POSTAL = re.compile(r"(?<!\d)\d{3}-\d{4}(?!\d)")
US_ZIP = re.compile(r"(?<![\d-])\d{5}(?:-\d{4})?(?![\d-])")
CN_POSTAL = re.compile(r"(?<!\d)\d{6}(?!\d)")
POSTAL_LABELS = {
    "en": re.compile(r"\b(?:postal|postal\s+code|zip(?:\s+code)?|postcode)\b", re.IGNORECASE),
    "ja": re.compile(r"(?:\bpostal\b|\bpostcode\b|\bzip\b|郵便番号|〒)", re.IGNORECASE),
    "zh": re.compile(r"(?:\bpostal\b|\bpostcode\b|\bzip\b|邮政编码|邮编|郵政編碼)", re.IGNORECASE),
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
    line_start, line_end = _line_bounds(text, start, end)
    line = text[line_start:line_end]
    if PHONE_LIKE.fullmatch(value.strip()) or DATE_LIKE.fullmatch(value.strip()):
        return True
    if _has_money_or_account_context(line, start - line_start):
        return True
    if language == "en" and not (_has_label(language, line) or _has_csv_header_context(language, text, line_start, line_end, start) or _looks_like_us_address_line(line)):
        return True
    if language == "ja" and not (_has_label(language, line) or "〒" in line or _has_csv_header_context(language, text, line_start, line_end, start) or _looks_like_jp_address_line(line)):
        return True
    if language == "zh" and not (_has_label(language, line) or _has_csv_header_context(language, text, line_start, line_end, start) or _looks_like_cn_address_line(line)):
        return True
    return False


def _line_for(text: str, start: int, end: int) -> str:
    line_start, line_end = _line_bounds(text, start, end)
    return text[line_start:line_end]


def _line_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end < 0:
        line_end = len(text)
    return line_start, line_end


def _has_label(language: str, line: str) -> bool:
    return bool(POSTAL_LABELS[language].search(line))


def _has_money_or_account_context(line: str, value_offset: int) -> bool:
    prefix = line[max(0, value_offset - 32) : value_offset]
    return bool(MONEY_OR_ACCOUNT_LABEL.search(prefix))


def _has_csv_header_context(language: str, text: str, line_start: int, line_end: int, absolute_start: int) -> bool:
    previous_start = text.rfind("\n", 0, max(0, line_start - 1))
    previous_start = 0 if previous_start < 0 else previous_start + 1
    previous_line = text[previous_start : max(0, line_start - 1)].strip("\r")
    current_line = text[line_start:line_end].strip("\r")
    if "," not in previous_line or "," not in current_line:
        return False
    column_index = _csv_column_for_offset(current_line, absolute_start - line_start)
    if column_index is None:
        return False
    try:
        header_cells = next(reader([previous_line]))
    except Exception:
        return False
    if column_index >= len(header_cells):
        return False
    return _has_label(language, header_cells[column_index])


def _csv_column_for_offset(line: str, offset: int) -> int | None:
    in_quotes = False
    column = 0
    start = 0
    index = 0
    while index <= len(line):
        char = line[index] if index < len(line) else ","
        if char == '"':
            if in_quotes and index + 1 < len(line) and line[index + 1] == '"':
                index += 2
                continue
            in_quotes = not in_quotes
        if (char == "," and not in_quotes) or index == len(line):
            if start <= offset <= index:
                return column
            column += 1
            start = index + 1
        index += 1
    return None


def _looks_like_us_address_line(line: str) -> bool:
    return bool(re.search(r"\b\d{1,6}\s+[A-Z][A-Za-z0-9 .'-]+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?)\b", line))


def _looks_like_jp_address_line(line: str) -> bool:
    return bool(re.search(r"(?:都|道|府|県).+(?:市|区|町|村).+\d", line))


def _looks_like_cn_address_line(line: str) -> bool:
    return bool(re.search(r"(?:省|市|自治区).+(?:区|县|路|街|号)", line))
