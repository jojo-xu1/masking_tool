from __future__ import annotations

from collections import defaultdict


class ReplacementMapper:
    def __init__(self) -> None:
        self._mapping: dict[tuple[str, str], str] = {}
        self._counts: dict[str, int] = defaultdict(int)

    def get(self, category: str, detected_text: str) -> str:
        key = (category, detected_text)
        if key not in self._mapping:
            self._counts[category] += 1
            self._mapping[key] = f"{category}_{self._counts[category]:03d}"
        return self._mapping[key]

    @property
    def mapping(self) -> dict[tuple[str, str], str]:
        return dict(self._mapping)
