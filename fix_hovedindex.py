#!/usr/bin/env python3
from pathlib import Path
import re

def safe_name(name: str) -> str:
    return name.replace(' ', '_').replace('ø', 'o').replace('æ', 'ae').replace('å', 'aa')

def main():
    html_path = Path("hovedindex.html")
    if not html_path.exists():
        print("hovedindex.html not found!")
        return

    content = html_path.read_text(encoding="utf-8")

    # Find all <a href="FOLDER/folder_index.html">
    def replace_link(match):
        folder = match.group(1)
        safe_folder = safe_name(folder)
        return f'href="{safe_folder}/folder_index.html"'

    new_content = re.sub(
        r'href="([^"/]+?)/folder_index\.html"',
        replace_link,
        content
    )

    html_path.write_text(new_content, encoding="utf-8")
    print("hovedindex.html links updated!")

if __name__ == "__main__":
    main()
