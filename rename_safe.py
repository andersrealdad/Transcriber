#!/usr/bin/env python3
"""
Rename ALL folders and files in input/ → URL-safe
FOLDERS FIRST, then files
"""

from pathlib import Path

# Mapping
CHAR_MAP = {
    ' ': '_',
    'ø': 'o', 'Ø': 'O',
    'æ': 'ae', 'Æ': 'AE',
    'å': 'aa', 'Å': 'AA',
}

def safe_name(name: str) -> str:
    for old, new in CHAR_MAP.items():
        name = name.replace(old, new)
    return name

def rename_path(path: Path) -> Path:
    if not path.exists():
        return path
    new_name = safe_name(path.name)
    if new_name == path.name:
        return path
    new_path = path.parent / new_name
    print(f"Renaming: {path} → {new_path.name}")
    path.rename(new_path)
    return new_path

def main():
    root = Path("input")
    if not root.exists():
        print("input/ folder not found!")
        return

    # Step 1: Rename folders (top-down)
    print("Renaming folders...")
    for folder in sorted(root.iterdir(), reverse=True):
        if folder.is_dir():
            rename_path(folder)

    # Step 2: Rename files inside
    print("\nRenaming files...")
    for file in root.rglob("*"):
        if file.is_file():
            rename_path(file)

    print("\nAll folders and files renamed!")
    print("Safe for file:// URLs")

if __name__ == "__main__":
    main()