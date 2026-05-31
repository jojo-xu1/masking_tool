from __future__ import annotations

from masking_tool.core.models import FileStatus, TargetFile


def apply_eligibility_status(target: TargetFile) -> TargetFile:
    if target.eligibility == "unsupported":
        target.status = FileStatus.SKIPPED_UNSUPPORTED
        target.failure_reason = "Unsupported extension"
    return target
