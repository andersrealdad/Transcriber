#!/usr/bin/env python3
"""
Generate ONE folder_index.html per folder (editable summaries + audio + transcript)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class FolderIndexGenerator:
    def __init__(
        self,
        input_root: str = "input",
        template_path: str = "template_editable_summaries.html",
    ):
        self.input_root = Path(input_root)
        self.template = Path(template_path).read_text(encoding="utf-8")

    # --------------------------------------------------------------------- #
    # 1. Find all real folders (skip hidden ones)
    # --------------------------------------------------------------------- #
    def get_folders(self) -> List[Path]:
        return [
            p
            for p in self.input_root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]

    # --------------------------------------------------------------------- #
    # 2. Pick the first *.txt → transcript
    # --------------------------------------------------------------------- #
    def find_transcript(self, folder: Path) -> Optional[Path]:
        txt_files = list(folder.glob("*.txt"))
        return txt_files[0] if txt_files else None

    # --------------------------------------------------------------------- #
    # 3. Pick the first audio file (m4a, mp3, wav …)
    # --------------------------------------------------------------------- #
    def find_audio(self, folder: Path) -> Optional[Path]:
        for ext in ("m4a", "mp3", "wav", "ogg", "flac"):
            audios = list(folder.glob(f"*.{ext}"))
            if audios:
                return audios[0]
        return None

    # --------------------------------------------------------------------- #
    # 4. Find all markdown summaries → language tabs
    # --------------------------------------------------------------------- #
    def find_summaries(self, folder: Path) -> List[Dict]:
        summaries = []
        seen_stems = set()

        for md_path in folder.glob("*.md"):
            stem = md_path.stem
            if stem in seen_stems:
                continue
            seen_stems.add(stem)

            # Split on the last '_' → language suffix
            parts = stem.rsplit("_", 1)
            base_name = parts[0]
            lang_code = parts[1] if len(parts) > 1 else "primary"
            lang_name = {
                "no": "Norsk",
                "en": "English",
                "primary": "Primær",
            }.get(lang_code, lang_code.title())

            summaries.append(
                {
                    "code": lang_code,
                    "name": lang_name,
                    "file": md_path.name,
                    "is_md": True,
                }
            )

        # Order: primary → no → others
        def sort_key(s):
            if s["code"] == "primary":
                return (0, "")
            if s["code"] == "no":
                return (1, "")
            return (2, s["code"])

        return sorted(summaries, key=sort_key)

    # --------------------------------------------------------------------- #
    # 5. Build the HTML for ONE folder
    # --------------------------------------------------------------------- #
    def generate_folder_index(self, folder: Path):
        folder_name = folder.name
        transcript = self.find_transcript(folder)
        audio = self.find_audio(folder)
        summaries = self.find_summaries(folder)

        if not transcript:
            print(f"Skipping {folder_name}: no .txt file")
            return

        # ---- date from folder name (DDMMYY) ---------------------------------
        try:
            date_part = folder_name.split(" - ")[0]
            day, mon, yr = date_part[:2], date_part[2:4], date_part[4:6]
            date_str = f"{day}.{mon}.20{yr}"
        except Exception:
            date_str = "Ukjent dato"

        # ---- audio player ----------------------------------------------------
        audio_html = ""
        if audio:
            ext = audio.suffix[1:]
            mime = {
                "m4a": "mp4",
                "mp3": "mpeg",
                "wav": "wav",
                "ogg": "ogg",
                "flac": "flac",
            }.get(ext, "mpeg")
            audio_html = f'''
            <div class="audio-player">
                <h3>Lydfil</h3>
                <audio controls>
                    <source src="{audio.name}" type="audio/{mime}">
                    Din nettleser støtter ikke audio-elementet.
                </audio>
            </div>'''

        # ---- language tabs ---------------------------------------------------
        tabs = "\n".join(
            f'<button class="tab-button" id="btn-{s["code"]}" onclick="switchTab(\'{s["code"]}\')">{s["name"]}</button>'
            for s in summaries
        )

        # ---- tab contents ----------------------------------------------------
        contents = []
        for s in summaries:
            contents.append(
                f'''
                <div class="tab-content" id="tab-{s["code"]}">
                    <div class="summary-header">
                        <h3>{s["name"]} sammendrag</h3>
                        <div class="edit-controls">
                            <button class="btn btn-edit" id="edit-summary-{s["code"]}"
                                    onclick="enableSummaryEditing('{s["code"]}')">
                                Rediger
                            </button>
                            <button class="btn btn-save" id="save-summary-{s["code"]}"
                                    onclick="saveSummary('{s["code"]}')">
                                Lagre
                            </button>
                            <button class="btn btn-cancel" id="cancel-summary-{s["code"]}"
                                    onclick="cancelSummaryEditing('{s["code"]}')">
                                Avbryt
                            </button>
                        </div>
                    </div>
                    <div id="summary-display-{s["code"]}" class="summary-display"></div>
                    <textarea id="summary-editor-{s["code"]}" class="summary-editor"></textarea>
                </div>'''
            )

        # ---- fill the template ------------------------------------------------
        html = self.template
        html = html.replace("{{TITLE}}", folder_name)
        html = html.replace("{{DATE}}", date_str)
        html = html.replace("{{AUDIO_PLAYER}}", audio_html)
        html = html.replace("{{SUMMARY_TABS}}", tabs)
        html = html.replace("{{SUMMARY_CONTENTS}}", "\n".join(contents))
        html = html.replace("{{BASE_NAME}}", transcript.stem)          # for JS transcript load
        html = html.replace("{{AVAILABLE_SUMMARIES}}", json.dumps(summaries))
        html = html.replace("{{CONTACT_NAME}}", "Anders Iversen")
        html = html.replace("{{CONTACT_PHONE}}", "+47 97 41 75 26")
        html = html.replace("{{CONTACT_GITHUB}}", "https://github.com/andersrealdad")

        out_path = folder / "folder_index.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"Generated: {out_path}")

    # --------------------------------------------------------------------- #
    # 6. Run on every folder
    # --------------------------------------------------------------------- #
    def run(self):
        folders = self.get_folders()
        print(f"Found {len(folders)} folders")
        for f in folders:
            self.generate_folder_index(f)
        print("All folder_index.html files generated!")


if __name__ == "__main__":
    FolderIndexGenerator().run()