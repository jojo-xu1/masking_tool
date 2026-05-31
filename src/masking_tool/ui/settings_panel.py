from __future__ import annotations


class SettingsPanelState:
    def __init__(self) -> None:
        self.rule_files: list[str] = []
        self.enabled: dict[str, bool] = {}
        self.person_detection_enabled = True
        self.phone_detection_enabled = True
        self.address_detection_enabled = True
        self.postal_code_detection_enabled = True
