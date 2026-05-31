from __future__ import annotations

from pathlib import Path


def main() -> int:
    required = [
        Path("pyproject.toml"),
        Path("src/masking_tool/__main__.py"),
        Path("src/masking_tool_defaults/en.yml"),
        Path("src/masking_tool_defaults/ja.yml"),
        Path("src/masking_tool_defaults/zh.yml"),
        Path("specs/001-mask-sensitive-strings/quickstart.md"),
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("Missing quickstart prerequisites:")
        for path in missing:
            print(f"- {path}")
        return 1
    print("Quickstart prerequisites are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
