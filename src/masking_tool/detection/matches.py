from __future__ import annotations

from dataclasses import dataclass

from masking_tool.core.models import MaskingRule, RuleType


@dataclass(frozen=True)
class DetectionMatch:
    rule: MaskingRule
    start: int
    end: int
    text: str
    line_context: str = ""

    @property
    def source_id(self) -> str:
        return self.rule.id

    @property
    def category(self) -> str:
        return self.rule.category


def match_priority(match: DetectionMatch) -> tuple[int, int, int]:
    explicit = 1 if match.rule.rule_type == RuleType.EXPLICIT else 0
    return (explicit, match.rule.risk_level.priority, -match.rule.order)


def line_context_for(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end < 0:
        line_end = len(text)
    return text[line_start:line_end].rstrip("\r")


def with_line_context(match: DetectionMatch, text: str) -> DetectionMatch:
    if match.line_context:
        return match
    return DetectionMatch(match.rule, match.start, match.end, match.text, line_context_for(text, match.start, match.end))


def attach_line_context(matches: list[DetectionMatch], text: str) -> list[DetectionMatch]:
    return [with_line_context(match, text) for match in matches]


def resolve_overlaps(matches: list[DetectionMatch]) -> list[DetectionMatch]:
    winners: list[DetectionMatch] = []
    for match in sorted(matches, key=lambda m: (m.start, m.end, m.rule.order)):
        overlapping = [w for w in winners if not (match.end <= w.start or match.start >= w.end)]
        if not overlapping:
            winners.append(match)
            continue

        best = max([match, *overlapping], key=match_priority)
        for old in overlapping:
            if old is not best and old in winners:
                winners.remove(old)
        if best is match and match not in winners:
            winners.append(match)
    return sorted(winners, key=lambda m: (m.start, m.end, m.rule.order))
