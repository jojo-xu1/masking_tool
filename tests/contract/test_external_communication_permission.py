from pathlib import Path

import pytest

from masking_tool.core.external_permission import (
    ExternalCommunicationDenied,
    ExternalCommunicationPermission,
    can_transmit,
    default_permission,
    require_permission,
)
from masking_tool.core.input_selection import make_file_selection
from masking_tool.core.models import InputSelection, MaskingRule, RiskLevel, RuleType, SelectionType
from masking_tool.core.processor import process


def test_default_permission_denies_masking_related_content() -> None:
    permission = default_permission()

    assert not can_transmit(permission, "input_content", "example-service")
    assert not can_transmit(permission, "detected_terms", "example-service")
    with pytest.raises(ExternalCommunicationDenied):
        require_permission(permission, "report_content", "example-service")


def test_explicit_permission_allows_only_declared_content_and_service() -> None:
    permission = ExternalCommunicationPermission.allow(
        {"detected_terms", "replacement_suggestions"},
        "approved-service",
        "user approved review export",
    )

    assert can_transmit(permission, "detected_terms", "approved-service")
    assert can_transmit(permission, "replacement_suggestions", "approved-service")
    assert not can_transmit(permission, "input_content", "approved-service")
    assert not can_transmit(permission, "detected_terms", "other-service")


def test_permission_rejects_unknown_content_type() -> None:
    with pytest.raises(ValueError, match="Unsupported external communication content"):
        ExternalCommunicationPermission.allow({"unknown"}, "approved-service", "test")


def test_default_masking_run_does_not_require_external_permission(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Secret", encoding="utf-8")
    rule = MaskingRule(
        "secret",
        "en",
        True,
        RuleType.EXPLICIT,
        "SECRET",
        RiskLevel.HIGH,
        "test literal",
        "replace",
        0,
        literal="Secret",
    )

    output_dir, _ = process(make_file_selection(source, "en", tmp_path / "output"), [rule])

    assert (output_dir / "files" / "sample.txt").read_text(encoding="utf-8") == "SECRET_001"


def test_processing_accepts_explicit_external_permission_without_changing_local_output(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Secret", encoding="utf-8")
    selection = InputSelection(
        SelectionType.FILE,
        source,
        tmp_path / "output",
        "en",
        None,
        ExternalCommunicationPermission.allow({"report_content"}, "approved-service", "test approval"),
    )
    rule = MaskingRule(
        "secret",
        "en",
        True,
        RuleType.EXPLICIT,
        "SECRET",
        RiskLevel.HIGH,
        "test literal",
        "replace",
        0,
        literal="Secret",
    )

    output_dir, _ = process(selection, [rule])

    assert (output_dir / "files" / "sample.txt").read_text(encoding="utf-8") == "SECRET_001"
