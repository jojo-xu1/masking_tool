from __future__ import annotations

from datetime import datetime
from pathlib import Path


def build_run_id(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%Y%m%d-%H%M%S")


def create_run_output_dir(output_root: Path, run_id: str | None = None) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    base_id = run_id or build_run_id()
    candidate = output_root / base_id
    if not candidate.exists():
        candidate.mkdir(parents=True)
        (candidate / "files").mkdir()
        return candidate

    index = 1
    while True:
        suffixed = output_root / f"{base_id}_{index:03d}"
        if not suffixed.exists():
            suffixed.mkdir(parents=True)
            (suffixed / "files").mkdir()
            return suffixed
        index += 1
