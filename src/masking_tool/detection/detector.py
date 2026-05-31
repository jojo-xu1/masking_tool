from __future__ import annotations

from pathlib import Path

from masking_tool.core.models import DetectionResult, MaskingRule, TargetFile
from masking_tool.detection.person import find_person_matches
from masking_tool.detection.phone import find_phone_matches
from masking_tool.detection.rules import find_rule_matches, resolve_conflicts
from masking_tool.replacement.mapping import ReplacementMapper


def context_for(text: str, start: int, end: int, radius: int = 20) -> str:
    return text[max(0, start - radius) : min(len(text), end + radius)]


def detect_text(
    target: TargetFile,
    text: str,
    rules: list[MaskingRule],
    mapper: ReplacementMapper,
    start_no: int = 1,
) -> list[DetectionResult]:
    language_rules = [r for r in rules if r.language == target.applied_language and r.enabled]
    matches = resolve_conflicts(
        [
            *find_rule_matches(text, language_rules),
            *find_person_matches(target, text, language_rules),
            *find_phone_matches(text, language_rules),
        ]
    )
    detections: list[DetectionResult] = []
    for index, match in enumerate(matches, start_no):
        replacement = mapper.get(match.rule.category, match.text)
        detections.append(
            DetectionResult(
                no=index,
                target_file=target,
                rule=match.rule,
                detected_text=match.text,
                replacement=replacement,
                context=context_for(text, match.start, match.end),
                span=(match.start, match.end),
            )
        )
    return detections
