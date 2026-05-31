from __future__ import annotations

from masking_tool.core.models import DetectionResult, MaskingRule, TargetFile
from masking_tool.detection.address import find_address_matches
from masking_tool.detection.matches import attach_line_context
from masking_tool.detection.person import find_person_matches
from masking_tool.detection.phone import find_phone_matches
from masking_tool.detection.postal import find_postal_matches
from masking_tool.detection.rules import find_rule_matches, resolve_conflicts
from masking_tool.replacement.mapping import ReplacementMapper


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
            *find_postal_matches(text, language_rules),
            *find_address_matches(text, language_rules),
        ]
    )
    matches = attach_line_context(matches, text)
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
                context=match.line_context,
                span=(match.start, match.end),
            )
        )
    return detections
