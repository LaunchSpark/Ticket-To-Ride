#!/usr/bin/env python3
"""
rename_spaces.py
Rename every file in the current directory whose name contains a space,
replacing all spaces with a hyphen (“-”).  If the intended new name
already exists, append -1, -2, … before the extension to avoid
overwriting.
"""

from pathlib import Path

def unique_target(original: Path) -> Path:
    """Return a collision-free Path for *original* after space→hyphen substitution."""
    base = Path(original.parent, original.name.replace(" ", "-"))
    if not base.exists():
        return base

    stem, suffix = base.stem, base.suffix
    i = 1
    while True:
        candidate = base.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1

def rename_files_with_spaces(directory: Path = Path(".")) -> None:
    renamed = skipped = 0
    for item in directory.iterdir():
        if item.is_file() and " " in item.name:          # ← only files with spaces
            target = unique_target(item)
            item.rename(target)
            print(f"✔  {item.name} → {target.name}")
            renamed += 1
        else:
            skipped += 1

    print("\nSummary:")
    print(f"  Renamed : {renamed}")
    print(f"  Skipped : {skipped}")

if __name__ == "__main__":
    rename_files_with_spaces()
