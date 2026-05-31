from __future__ import annotations

import re


JAPANESE_PHONE_PATTERN = re.compile(r"(?:\b0\d{1,4}-\d{1,4}-\d{3,4}\b|\b0[789]0\d{8}\b)")
JAPANESE_MARKERS = ("氏名", "名前", "電話", "メール", "住所", "会社", "部署", "担当", "承認", ".jp")


def detect_language(text: str) -> tuple[str | None, float]:
    if not any(char.isalpha() or "\u3040" <= char <= "\u30ff" or "\u4e00" <= char <= "\u9fff" for char in text):
        return None, 0.0
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        # Han characters can be Japanese or Chinese. Kana gives a strong Japanese signal.
        if any("\u3040" <= char <= "\u30ff" for char in text):
            return "ja", 0.95
        if JAPANESE_PHONE_PATTERN.search(text) or any(marker in text for marker in JAPANESE_MARKERS):
            return "ja", 0.88
        return "zh", 0.80
    return "en", 0.70
