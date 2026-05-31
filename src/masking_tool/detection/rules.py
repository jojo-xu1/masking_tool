from __future__ import annotations

import re

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType
from masking_tool.detection.matches import DetectionMatch, resolve_overlaps

RuleMatch = DetectionMatch


def find_rule_matches(text: str, rules: list[MaskingRule]) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    for rule in rules:
        if not rule.enabled:
            continue
        if rule.rule_type == RuleType.EXPLICIT and rule.literal:
            start = 0
            while True:
                index = text.find(rule.literal, start)
                if index < 0:
                    break
                matches.append(DetectionMatch(rule, index, index + len(rule.literal), rule.literal))
                start = index + len(rule.literal)
        elif rule.rule_type == RuleType.REGEX and rule.pattern:
            for match in re.finditer(rule.pattern, text):
                matches.append(DetectionMatch(rule, match.start(), match.end(), match.group(0)))
    return sorted(matches, key=lambda m: (m.start, m.end, m.rule.order))


def resolve_conflicts(matches: list[RuleMatch]) -> list[RuleMatch]:
    return resolve_overlaps(matches)
