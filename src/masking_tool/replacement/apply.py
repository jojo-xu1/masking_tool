from __future__ import annotations

from masking_tool.core.models import DetectionResult


def apply_replacements(text: str, detections: list[DetectionResult]) -> str:
    result = text
    for detection in sorted(detections, key=lambda d: d.span[0], reverse=True):
        start, end = detection.span
        result = result[:start] + detection.replacement + result[end:]
    return result
