from __future__ import annotations

import re

from masking_tool.core.models import MaskingRule, RuleType
from masking_tool.detection.matches import DetectionMatch


PHONE_PATTERN = re.compile(
    r"""
    (?<![A-Za-z0-9])
    (?:
      (?:\+81[-\s]?)?(?:0\d{1,4})[-\s]?\d{2,4}[-\s]?\d{3,4}
      |
      (?:\+1[-\s]?)?(?:\(?[2-9]\d{2}\)?[-\s]?)\d{3}[-\s]?\d{4}
      |
      (?:\+86[-\s]?)?(?:1[3-9]\d{9}|10[-\s]?\d{4}[-\s]?\d{4})
    )
    (?![A-Za-z0-9])
    """,
    re.VERBOSE,
)
DATE_PATTERN = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
JP_POSTAL_PATTERN = re.compile(r"^\d{3}-\d{4}$")


def find_phone_matches(text: str, rules: list[MaskingRule]) -> list[DetectionMatch]:
    matches: list[DetectionMatch] = []
    for rule in rules:
        if not rule.enabled or rule.rule_type != RuleType.PHONE:
            continue
        for match in PHONE_PATTERN.finditer(text):
            value = match.group(0).strip()
            if _is_false_positive(value):
                continue
            matches.append(DetectionMatch(rule, match.start(), match.end(), value))
    return matches


def _is_false_positive(value: str) -> bool:
    normalized = re.sub(r"\D", "", value)
    if DATE_PATTERN.match(value) or JP_POSTAL_PATTERN.match(value):
        return True
    if len(normalized) < 10 or len(normalized) > 15:
        return True
    if len(set(normalized)) == 1:
        return True
    return False
