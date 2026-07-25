#!/usr/bin/env python3
"""
sync_edit_templates.py — Keep the "Edit a …" issue forms' ID dropdowns in sync with the data.

The edit-* issue templates let a contributor pick an existing entry from a dropdown
instead of typing its id by hand. That option list has to mirror data/*.yaml, so this
script regenerates it from the YAML files.

Only the lines between the AUTOGEN markers are rewritten:

    options:
      # AUTOGEN:models:start
      - "lerobot — LeRobot"
      # AUTOGEN:models:end

Each option is rendered as "<id> — <name>"; process_issue.py keeps only the id.

Run automatically by .github/workflows/sync-edit-dropdowns.yml whenever data/ changes
on main. Also useful locally:

  python scripts/sync_edit_templates.py
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"

# (data file, issue template, marker name)
JOBS = [
    ("models.yaml", "edit-model.yml", "models"),
    ("datasets.yaml", "edit-dataset.yml", "datasets"),
    ("tools.yaml", "edit-simulator.yml", "tools"),
]

OPTION_INDENT = " " * 8


def yaml_quote(value: str) -> str:
    """Render a string as a YAML double-quoted scalar."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def options_block(entries: list[dict]) -> str:
    lines = []
    for entry in entries:
        entry_id = str(entry.get("id", "")).strip()
        if not entry_id:
            continue
        name = str(entry.get("name", "")).strip()
        label = f"{entry_id} — {name}" if name else entry_id
        lines.append(f"{OPTION_INDENT}- {yaml_quote(label)}")
    return "\n".join(lines)


def sync(data_name: str, template_name: str, marker: str) -> bool:
    """Rewrite one template's option block. Returns True if the file changed."""
    data_path = DATA_DIR / data_name
    template_path = TEMPLATE_DIR / template_name

    if not data_path.exists():
        print(f"::warning::{data_path.name} not found — skipping {template_name}")
        return False
    if not template_path.exists():
        print(f"::warning::{template_name} not found — skipping")
        return False

    with open(data_path, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []

    block = options_block(entries)
    if not block:
        print(f"::warning::{data_name} has no usable entries — leaving {template_name} alone")
        return False

    text = template_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(^[ \t]*# AUTOGEN:{re.escape(marker)}:start[ \t]*\n).*?(^[ \t]*# AUTOGEN:{re.escape(marker)}:end)",
        re.DOTALL | re.MULTILINE,
    )
    new_text, count = pattern.subn(lambda m: m.group(1) + block + "\n" + m.group(2), text)
    if count == 0:
        print(f"::error::AUTOGEN:{marker} markers not found in {template_name}")
        sys.exit(1)

    if new_text == text:
        print(f"  {template_name}: already up to date ({len(entries)} entries)")
        return False

    template_path.write_text(new_text, encoding="utf-8")
    print(f"  {template_name}: synced {len(entries)} entries")
    return True


def main() -> int:
    print("=== Syncing edit-form ID dropdowns ===")
    changed = [sync(*job) for job in JOBS]
    print("✅ Templates updated" if any(changed) else "✅ Nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
