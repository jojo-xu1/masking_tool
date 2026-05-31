from __future__ import annotations


def detect_language(text: str) -> tuple[str | None, float]:
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        # Han characters can be Japanese or Chinese. Kana gives a strong Japanese signal.
        if any("\u3040" <= char <= "\u30ff" for char in text):
            return "ja", 0.95
        return "zh", 0.80
    return "en", 0.70
