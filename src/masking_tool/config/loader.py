from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from masking_tool.core.models import MaskingRule, RiskLevel, RuleType, SUPPORTED_LANGUAGES


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyYAML is required to load rule configuration") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Rule file must contain a mapping: {path}")
    return data


def load_rule_file(path: str | Path, starting_order: int = 0) -> list[MaskingRule]:
    path = Path(path)
    data = _load_yaml(path)
    language = data.get("language")
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported rule language in {path}: {language}")
    rules_data = data.get("rules")
    if not isinstance(rules_data, list):
        raise ValueError(f"Rule file must contain rules list: {path}")
    sources_data = data.get("sources", [])
    if sources_data is None:
        sources_data = []
    if not isinstance(sources_data, list):
        raise ValueError(f"Rule file sources must be a list: {path}")

    rules: list[MaskingRule] = []
    seen: set[str] = set()
    for offset, raw in enumerate([*rules_data, *sources_data]):
        if not isinstance(raw, dict):
            raise ValueError("Each rule must be a mapping")
        rule_id = str(raw.get("id", "")).strip()
        if not rule_id:
            raise ValueError("Rule id is required")
        if rule_id in seen:
            raise ValueError(f"Duplicate rule id in {path}: {rule_id}")
        seen.add(rule_id)

        rule_type = RuleType(str(raw.get("type")))
        risk_level = RiskLevel(str(raw.get("risk_level")))
        pattern = raw.get("pattern")
        literal = raw.get("literal")
        if rule_type == RuleType.REGEX:
            if not pattern:
                raise ValueError(f"Regex rule requires pattern: {rule_id}")
            re.compile(str(pattern))
        if rule_type == RuleType.EXPLICIT and not literal:
            raise ValueError(f"Explicit rule requires literal: {rule_id}")
        if rule_type in {RuleType.PERSON, RuleType.PHONE, RuleType.ADDRESS, RuleType.POSTAL_CODE} and (pattern or literal):
            raise ValueError(f"Detection source does not accept pattern or literal: {rule_id}")

        rules.append(
            MaskingRule(
                id=rule_id,
                language=language,
                enabled=bool(raw.get("enabled", False)),
                rule_type=rule_type,
                pattern=str(pattern) if pattern is not None else None,
                literal=str(literal) if literal is not None else None,
                category=str(raw["category"]),
                risk_level=risk_level,
                judgment_reason=str(raw["judgment_reason"]),
                recommended_action=str(raw["recommended_action"]),
                order=starting_order + offset,
                model_name=str(raw["model_name"]) if raw.get("model_name") is not None else None,
                unavailable_behavior=str(raw.get("unavailable_behavior", "skip_with_reason")),
                required=bool(raw.get("required", False)),
            )
        )
    return rules


def load_rule_files(paths: list[str | Path]) -> list[MaskingRule]:
    rules: list[MaskingRule] = []
    seen: set[str] = set()
    for path in paths:
        next_rules = load_rule_file(path, len(rules))
        for rule in next_rules:
            if rule.id in seen:
                raise ValueError(f"Duplicate rule id across files: {rule.id}")
            seen.add(rule.id)
        rules.extend(next_rules)
    return rules
