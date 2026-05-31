from __future__ import annotations

from pathlib import Path

from masking_tool.config.loader import load_rule_files
from masking_tool.core.models import MaskingRule


def load_effective_rules(default_paths: list[Path], user_paths: list[Path] | None = None) -> list[MaskingRule]:
    return load_rule_files([*default_paths, *(user_paths or [])])
