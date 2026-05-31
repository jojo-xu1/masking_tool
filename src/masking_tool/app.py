from __future__ import annotations


def main() -> int:
    """Start the desktop app when PySide6 is available."""
    try:
        from masking_tool.ui.main_window import run_app
    except Exception as exc:  # pragma: no cover - fallback for minimal envs
        print(f"UI is unavailable: {exc}")
        return 1
    return run_app()
