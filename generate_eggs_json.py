#!/usr/bin/env python3
"""Generate eggs.json with categories and Egg names from this repository.

Category rule:
- Use the first folder name.
- If there is a second folder, use "<first> <second>".
- Ignore third-level and deeper folder names.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT / "eggs.json"


def is_egg_definition(data: Any) -> bool:
    """Heuristic to identify a Pterodactyl Egg definition JSON."""
    if not isinstance(data, dict):
        return False

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return False

    # Typical Egg files contain these structures; this filters out config JSONs.
    has_egg_keys = any(key in data for key in ("startup", "docker_images", "variables", "config"))
    return has_egg_keys


def category_from_path(path: Path, root: Path) -> str | None:
    rel = path.relative_to(root)
    parts = rel.parts[:-1]  # directories only

    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[1]}"


def collect_eggs(root: Path) -> list[dict[str, Any]]:
    categories: dict[str, set[str]] = {}

    for json_file in root.rglob("*.json"):
        if json_file.name == OUTPUT_FILE.name:
            continue
        if ".git" in json_file.parts:
            continue

        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not is_egg_definition(data):
            continue

        category = category_from_path(json_file, root)
        if category is None:
            continue

        egg_name = data["name"].strip()
        categories.setdefault(category, set()).add(egg_name)

    result = []
    for category in sorted(categories):
        result.append(
            {
                "category": category,
                "eggs": sorted(categories[category], key=str.casefold),
            }
        )

    return result


def main() -> None:
    output = collect_eggs(ROOT)
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE} ({len(output)} categories)")


if __name__ == "__main__":
    main()
