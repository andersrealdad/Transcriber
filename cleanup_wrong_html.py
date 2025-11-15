#!/usr/bin/env python3
"""
Remove all old/wrong HTML files — keep only folder_index.html
"""

from pathlib import Path

# Where your input folders are
INPUT_ROOT = Path("input")

def main():
    removed = 0
    for folder in INPUT_ROOT.iterdir():
        if not folder.is_dir():
            continue
        for html_file in folder.glob("*.html"):
            if html_file.name != "folder_index.html":
                print(f"Removing: {html_file}")
                html_file.unlink()
                removed += 1
    print(f"\nDone! Removed {removed} old HTML files.")
    print("Only folder_index.html remains in each folder.")

if __name__ == "__main__":
    main()