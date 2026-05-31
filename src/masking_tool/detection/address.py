from __future__ import annotations

import re

from masking_tool.core.models import MaskingRule, RuleType
from masking_tool.detection.matches import DetectionMatch


LABELS = {
    "en": re.compile(r"\b(?:address|mailing address|office address)\s*[:=]\s*(?P<value>[^\r\n,]+(?:,[^\r\n]+)?)", re.IGNORECASE),
    "ja": re.compile(r"(?:住所|所在地)\s*[:：]\s*(?P<value>[^\r\n]+)"),
    "zh": re.compile(r"(?:地址|住址|办公地址)\s*[:：]\s*(?P<value>[^\r\n]+)"),
}
STRUCTURES = {
    "en": re.compile(r"(?P<value>\b\d{1,6}\s+[A-Z][A-Za-z0-9 .'-]+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?)\b(?:,\s*[A-Z][A-Za-z .'-]+,\s*[A-Z]{2})?)"),
    "ja": re.compile(r"(?P<value>(?:東京都|北海道|大阪府|京都府|.{2,3}県).{1,30}(?:市|区|町|村).{0,40}?\d{1,4}(?:-\d{1,4}){0,2})"),
    "zh": re.compile(r"(?P<value>(?:北京市|上海市|天津市|重庆市|.{2,8}省|.{2,8}自治区).{1,40}(?:区|县|市).{0,40}?(?:路|街|号).{0,20})"),
}
POSTAL_PREFIX = {
    "en": re.compile(r"^\s*(?:postal\s+code|zip(?:\s+code)?|postcode)?\s*\d{5}(?:-\d{4})?\s*", re.IGNORECASE),
    "ja": re.compile(r"^\s*(?:〒|郵便番号\s*[:：]?\s*)?\d{3}-\d{4}\s*"),
    "zh": re.compile(r"^\s*(?:邮政编码|邮编|郵政編碼)?\s*[:：]?\s*\d{6}\s*"),
}


def find_address_matches(text: str, rules: list[MaskingRule]) -> list[DetectionMatch]:
    matches: list[DetectionMatch] = []
    for rule in rules:
        if not rule.enabled or rule.rule_type != RuleType.ADDRESS:
            continue
        matches.extend(_label_matches(rule, text))
        matches.extend(_structure_matches(rule, text))
    return _dedupe(matches)


def _label_matches(rule: MaskingRule, text: str) -> list[DetectionMatch]:
    pattern = LABELS.get(rule.language)
    if pattern is None:
        return []
    matches: list[DetectionMatch] = []
    for match in pattern.finditer(text):
        start, end, value = _trim_address_value(rule.language, match.group("value"), match.start("value"))
        if value:
            matches.append(DetectionMatch(rule, start, end, value))
    return matches


def _structure_matches(rule: MaskingRule, text: str) -> list[DetectionMatch]:
    pattern = STRUCTURES.get(rule.language)
    if pattern is None:
        return []
    matches: list[DetectionMatch] = []
    for match in pattern.finditer(text):
        start, end, value = _trim_address_value(rule.language, match.group("value"), match.start("value"))
        if value:
            matches.append(DetectionMatch(rule, start, end, value))
    return matches


def _trim_address_value(language: str, value: str, start: int) -> tuple[int, int, str]:
    cleaned = value.strip(" \t,，")
    start += len(value) - len(value.lstrip(" \t,，"))
    prefix = POSTAL_PREFIX[language].match(cleaned)
    if prefix:
        start += prefix.end()
        cleaned = cleaned[prefix.end() :].strip(" \t,，")
    cleaned = re.split(r"\s+(?:phone|tel|email|date)\s*[:=]", cleaned, maxsplit=1, flags=re.IGNORECASE)[0]
    cleaned = re.split(r"(?:電話|メール|日期|电话|邮箱)\s*[:：]", cleaned, maxsplit=1)[0]
    cleaned = cleaned.strip(" \t,，")
    return start, start + len(cleaned), cleaned


def _dedupe(matches: list[DetectionMatch]) -> list[DetectionMatch]:
    unique: list[DetectionMatch] = []
    seen: set[tuple[int, int, str]] = set()
    for match in sorted(matches, key=lambda item: (item.start, item.end, item.rule.order)):
        key = (match.start, match.end, match.text)
        if key not in seen:
            unique.append(match)
            seen.add(key)
    return unique
