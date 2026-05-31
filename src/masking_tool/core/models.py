from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from masking_tool.core.external_permission import ExternalCommunicationPermission


SUPPORTED_EXTENSIONS = {".txt", ".csv", ".log", ".docx", ".xlsx", ".pptx", ".pdf"}
SUPPORTED_LANGUAGES = {"en", "ja", "zh"}


class SelectionType(str, Enum):
    FILE = "file"
    FOLDER = "folder"


class RuleType(str, Enum):
    REGEX = "regex"
    EXPLICIT = "explicit"
    PERSON = "person"
    PHONE = "phone"


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def priority(self) -> int:
        return {RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}[self]


class FileStatus(str, Enum):
    DISCOVERED = "discovered"
    PROCESSED = "processed"
    NO_REPLACEMENT = "no_replacement"
    SKIPPED_UNSUPPORTED = "skipped_unsupported"
    SKIPPED_OUT_OF_SCOPE = "skipped_out_of_scope"
    FAILED = "failed"


class RunStatus(str, Enum):
    COMPLETED = "completed"
    COMPLETED_WITH_FAILURES = "completed_with_failures"
    FAILED_VALIDATION = "failed_validation"


@dataclass(frozen=True)
class InputSelection:
    selection_type: SelectionType
    input_path: Path
    output_root: Path = Path("output")
    single_file_language: str | None = None
    folder_language_mode: str | None = None
    external_permission: "ExternalCommunicationPermission | None" = None


@dataclass(frozen=True)
class ProcessingRun:
    run_id: str
    started_at: datetime
    output_dir: Path
    settings_snapshot: dict[str, Any] = field(default_factory=dict)
    status: RunStatus = RunStatus.COMPLETED


@dataclass
class TargetFile:
    source_path: Path
    relative_path: Path
    extension: str
    eligibility: str
    applied_language: str | None = None
    language_confidence: float | None = None
    status: FileStatus = FileStatus.DISCOVERED
    output_path: Path | None = None
    failure_reason: str | None = None


@dataclass(frozen=True)
class MaskingRule:
    id: str
    language: str
    enabled: bool
    rule_type: RuleType
    category: str
    risk_level: RiskLevel
    judgment_reason: str
    recommended_action: str
    order: int
    pattern: str | None = None
    literal: str | None = None
    model_name: str | None = None
    unavailable_behavior: str = "skip_with_reason"
    required: bool = False


@dataclass
class DetectionResult:
    no: int
    target_file: TargetFile
    rule: MaskingRule
    detected_text: str
    replacement: str
    context: str
    span: tuple[int, int]

    @property
    def category(self) -> str:
        return self.rule.category

    @property
    def risk_level(self) -> RiskLevel:
        return self.rule.risk_level
