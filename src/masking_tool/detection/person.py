from __future__ import annotations

import re
from typing import Any

from masking_tool.core.models import MaskingRule, RuleType, TargetFile
from masking_tool.detection.matches import DetectionMatch


class PersonDetectionUnavailable(RuntimeError):
    pass


_MODEL_CACHE: dict[str, Any] = {}
PERSON_LABELS = {"PERSON", "PER"}
ASCII_ALNUM = re.compile(r"[A-Za-z0-9]")
HAN = r"\u4e00-\u9fff"
KANA = r"\u3040-\u30ff"
JAPANESE_SURNAMES = (
    "佐藤鈴木高橋田中伊藤渡辺山本中村小林加藤吉田山田佐々木山口松本井上木村林"
    "清水山崎森池田橋本阿部石川山下中島前田藤田小川後藤岡田長谷川村上近藤"
    "石井斎藤坂本遠藤青木藤井西村福田太田三浦藤原岡本松田中川中野原田小野"
)
JAPANESE_NAME = rf"(?:佐々木|長谷川|[{JAPANESE_SURNAMES}][{HAN}]?)[{HAN}]{{1,3}}"
JAPANESE_LABEL_PATTERN = re.compile(
    rf"(?:owner|reviewer|name|氏名|名前|担当者|承認者|申請者|連絡先)\s*[=:：]\s*(?P<name>{JAPANESE_NAME})",
    re.IGNORECASE,
)
JAPANESE_DELIMITED_PATTERN = re.compile(rf"(?:(?<=^)|(?<=[,\s]))(?P<name>{JAPANESE_NAME})(?=(?:[,。\s]|$))")
CHINESE_SURNAMES = (
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
    "谢邹喻柏潘葛范彭郎鲁韦昌马苗方俞任袁柳鲍史唐费廉岑薛雷贺倪汤"
    "罗毕郝安常于傅齐康伍余元顾孟平黄穆萧尹姚邵汪毛戴宋庞熊纪舒屈"
    "项祝董梁杜阮蓝季贾路江童颜郭梅林钟徐邱高夏蔡田胡凌霍虞万卢莫"
    "解应宗丁宣邓洪包左石崔龚程邢裴陆荣翁甄家段侯全秋伊宁甘祖武刘"
    "景詹龙叶黎白赖乔闻谭申冉牛温庄柴瞿阎连鱼向古易戈廖衡耿文寇"
)
CHINESE_NAME = rf"[{CHINESE_SURNAMES}][{HAN}]{{1,2}}"
CHINESE_LABEL_PATTERN = re.compile(
    rf"(?:负责人|联系人|姓名|客户|审批人|经办人|申请人|报告人|员工|经理|主管)\s*[:：]\s*(?P<name>{CHINESE_NAME})"
)
CHINESE_CONTEXT_PATTERN = re.compile(
    rf"(?<![{HAN}])(?P<name>{CHINESE_NAME})(?=(?:的|批准|要求|联系|签署|负责|确认|同意|参加|发送|审核|处理|提交|。|，|、|；|;|\s|$))"
)


def load_spacy_model(model_name: str) -> Any:
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]
    try:
        import spacy
    except Exception as exc:  # pragma: no cover - depends on environment
        raise PersonDetectionUnavailable("spaCy is required for person-name detection") from exc
    try:
        model = spacy.load(model_name)
    except Exception as exc:  # pragma: no cover - depends on installed models
        raise PersonDetectionUnavailable(f"spaCy model is unavailable: {model_name}") from exc
    _MODEL_CACHE[model_name] = model
    return model


def find_person_matches(target: TargetFile, text: str, rules: list[MaskingRule]) -> list[DetectionMatch]:
    matches: list[DetectionMatch] = []
    for rule in rules:
        if not rule.enabled or rule.rule_type != RuleType.PERSON:
            continue
        model_name = rule.model_name or _default_model_name(rule.language)
        try:
            doc = load_spacy_model(model_name)(text)
        except PersonDetectionUnavailable as exc:
            message = str(exc)
            if rule.language == "zh" and rule.unavailable_behavior in {"fallback_heuristic", "skip_with_reason"}:
                matches.extend(_find_chinese_fallback_matches(rule, text))
                continue
            if rule.required or rule.unavailable_behavior == "fail":
                raise PersonDetectionUnavailable(message) from exc
            target.failure_reason = message
            continue
        for ent in getattr(doc, "ents", []):
            if str(getattr(ent, "label_", "")).upper() not in PERSON_LABELS:
                continue
            entity_text = str(getattr(ent, "text", ""))
            if not entity_text.strip() or not _is_candidate_for_language(rule.language, entity_text):
                continue
            matches.extend(_matches_for_all_occurrences(rule, text, entity_text))
        if rule.language == "ja":
            matches.extend(_find_japanese_fallback_matches(rule, text))
    return _dedupe_matches(matches)


def _find_japanese_fallback_matches(rule: MaskingRule, text: str) -> list[DetectionMatch]:
    names: list[str] = []
    for pattern in (JAPANESE_LABEL_PATTERN, JAPANESE_DELIMITED_PATTERN):
        for match in pattern.finditer(text):
            name = match.group("name")
            if name not in names:
                names.append(name)

    matches: list[DetectionMatch] = []
    for name in names:
        matches.extend(_matches_for_all_occurrences(rule, text, name))
    return matches


def _find_chinese_fallback_matches(rule: MaskingRule, text: str) -> list[DetectionMatch]:
    names: list[str] = []
    for pattern in (CHINESE_LABEL_PATTERN, CHINESE_CONTEXT_PATTERN):
        for match in pattern.finditer(text):
            name = match.group("name")
            if name not in names:
                names.append(name)

    matches: list[DetectionMatch] = []
    seen: set[tuple[int, int, str]] = set()
    for name in names:
        for match in _matches_for_all_occurrences(rule, text, name):
            key = (match.start, match.end, match.text)
            if key not in seen:
                matches.append(match)
                seen.add(key)
    return sorted(matches, key=lambda match: (match.start, match.end))


def _matches_for_all_occurrences(rule: MaskingRule, text: str, entity_text: str) -> list[DetectionMatch]:
    value = entity_text.strip()
    matches: list[DetectionMatch] = []
    start = 0
    while True:
        index = text.find(value, start)
        if index < 0:
            break
        end = index + len(value)
        if _has_person_boundaries(text, index, end):
            matches.append(DetectionMatch(rule, index, end, value))
        start = index + len(value)
    return matches


def _dedupe_matches(matches: list[DetectionMatch]) -> list[DetectionMatch]:
    unique: list[DetectionMatch] = []
    seen: set[tuple[int, int, str, str]] = set()
    for match in matches:
        key = (match.start, match.end, match.text, match.rule.id)
        if key in seen:
            continue
        unique.append(match)
        seen.add(key)
    return sorted(unique, key=lambda match: (match.start, match.end))


def _is_candidate_for_language(language: str, value: str) -> bool:
    if language == "en":
        return bool(re.search(r"[A-Za-z]", value))
    if language == "ja":
        return bool(re.search(rf"[{HAN}{KANA}]", value))
    if language == "zh":
        return bool(re.search(rf"[{HAN}]", value))
    return bool(value.strip())


def _has_person_boundaries(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return not ASCII_ALNUM.match(before) and not ASCII_ALNUM.match(after)


def _default_model_name(language: str) -> str:
    return {
        "en": "en_core_web_sm",
        "ja": "ja_core_news_sm",
        "zh": "zh_core_web_sm",
    }.get(language, language)
