from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


MASKING_CONTENT_TYPES = frozenset(
    {
        "input_content",
        "detected_terms",
        "replacement_suggestions",
        "report_content",
    }
)


class ExternalCommunicationDenied(PermissionError):
    pass


@dataclass(frozen=True)
class ExternalCommunicationPermission:
    permitted: bool = False
    permitted_content: frozenset[str] = field(default_factory=frozenset)
    target_service: str | None = None
    permission_reason: str | None = None

    def __post_init__(self) -> None:
        content = frozenset(self.permitted_content)
        unknown = content - MASKING_CONTENT_TYPES
        if unknown:
            raise ValueError(f"Unsupported external communication content: {', '.join(sorted(unknown))}")
        object.__setattr__(self, "permitted_content", content)
        if self.permitted and not self.target_service:
            raise ValueError("Explicit external communication permission requires target_service")

    @classmethod
    def allow(
        cls,
        content: Iterable[str],
        target_service: str,
        permission_reason: str,
    ) -> ExternalCommunicationPermission:
        return cls(
            permitted=True,
            permitted_content=frozenset(content),
            target_service=target_service,
            permission_reason=permission_reason,
        )

    def allows(self, content: str, target_service: str) -> bool:
        return self.permitted and self.target_service == target_service and content in self.permitted_content


def default_permission() -> ExternalCommunicationPermission:
    return ExternalCommunicationPermission()


def can_transmit(
    permission: ExternalCommunicationPermission | None,
    content: str,
    target_service: str,
) -> bool:
    return (permission or default_permission()).allows(content, target_service)


def require_permission(
    permission: ExternalCommunicationPermission | None,
    content: str,
    target_service: str,
) -> None:
    if not can_transmit(permission, content, target_service):
        raise ExternalCommunicationDenied(
            f"External communication for {content} to {target_service} requires explicit user permission"
        )


def permission_snapshot(permission: ExternalCommunicationPermission | None) -> dict[str, object]:
    effective = permission or default_permission()
    return {
        "external_communication_permitted": effective.permitted,
        "permitted_content": sorted(effective.permitted_content),
        "target_service": effective.target_service,
        "permission_reason": effective.permission_reason,
    }
