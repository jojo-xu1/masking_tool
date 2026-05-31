from __future__ import annotations

from dataclasses import dataclass, field

from masking_tool.core.models import DetectionResult, FileStatus, TargetFile


@dataclass
class FileProcessingResult:
    target: TargetFile
    detections: list[DetectionResult] = field(default_factory=list)

    @property
    def status(self) -> FileStatus:
        return self.target.status


class ProcessingError(RuntimeError):
    """Processing error with a user-reportable reason."""
