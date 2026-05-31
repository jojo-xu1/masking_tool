from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RuleToggleState:
    enabled_by_id: dict[str, bool] = field(default_factory=dict)

    def is_enabled(self, rule_id: str, default: bool) -> bool:
        return self.enabled_by_id.get(rule_id, default)

    def is_source_enabled(self, source_id: str, default: bool) -> bool:
        return self.is_enabled(source_id, default)
