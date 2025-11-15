#!/usr/bin/env python3
"""
HTML Generator with Editable Summaries and Language Tabs
Generates HTML pages with TinyMCE editors for transcripts and summaries
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import argparse


class EditableHTMLGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup paths
        self.input_folder = Path(self.config['folders']['input'])
        self.output_folder = Path(self.config['folders']['output']) if self.config['folders']['output'] else None
        
        # Load template
        template_path = Path(__file__).parent / "template_editable_summaries.html"
        if not template_path.exists():
            # Fallback to current directory
            template_path = Path("template_editable_summaries.html")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def find_transcription_files(self) -> List[Path]:
        """Find all .txt transcription files"""
        txt_files = []
        
        if self.config['processing']['recursive']:
            pattern = "**/*.txt"
        else:
            pattern = "*.txt"
        
        for txt_file in self.input_folder.glob(pattern):
            if txt_file.is_file():
                txt_files.append(txt_file)
        
        return txt_files
    
    def find_summaries(self, base_path: Path) -> List[Dict[str, str]]:
        """Find all summary files for a given base path"""
        summaries = []
        base_name = base_path.stem
        parent = base_path.parent
        
        # Language mapping
        lang_names = {
            'no': 'Norsk',
            'en': 'English',
            'primary': 'Primær'
        }
        
        # Check for language-specific summaries
        # Look for .summary.txt (for HTML display) or .docx (for download)
        for lang_code in ['no', 'en', 'sv', 'da', 'de', 'fr', 'es']:
            # Prefer .summary.txt for HTML display
            summary_txt = parent / f"{base_name}_{lang_code}.summary.txt"
            summary_docx = parent / f"{base_name}_{lang_code}.docx"
            
            if summary_txt.exists():
                summaries.append({
                    'code': lang_code,
                    'name': lang_names.get(lang_code, lang_code.upper()),
                    'file': f"{base_name}_{lang_code}.summary.txt",
                    'docx_file': f"{base_name}_{lang_code}.docx" if summary_docx.exists() else None
                })
            elif summary_docx.exists():
                # Only .docx available (will show download link)
                summaries.append({
                    'code': lang_code,
                    'name': lang_names.get(lang_code, lang_code.upper()),
                    'file': f"{base_name}_{lang_code}.docx",
                    'docx_file': f"{base_name}_{lang_code}.docx"
                })
        
        # Check for primary summary (no language suffix)
        primary_txt = parent / f"{base_name}.summary.txt"
        primary_docx = parent / f"{base_name}.docx"
        
        if primary_txt.exists():
            summaries.insert(0, {
                'code': 'primary',
                'name': 'Primær',
                'file': f"{base_name}.summary.txt",
                'docx_file': f"{base_name}.docx" if primary_docx.exists() else None
            })
        elif primary_docx.exists():
            summaries.insert(0, {
                'code': 'primary',
                'name': 'Primær',
                'file': f"{base_name}.docx",
                'docx_file': f"{base_name}.docx"
            })
        
        return summaries
    
    def find_audio_file(self, base_path: Path) -> Optional[Path]:
        """Find corresponding audio file"""
        base_name = base_path.stem
        parent = base_path.parent
        
        # Check common audio formats
        for ext in ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'opus', 'webm', 'aac']:
            audio_path = parent / f"{base_name}.{ext}"
            if audio_path.exists():
                return audio_path
        
        return None
    
    def format_duration(self, audio_path: Path) -> str:
        """Get audio duration (simplified - returns file size as proxy)"""
        try:
            size_mb = audio_path.stat().st_size / (1024 * 1024)
            # Rough estimate: 1MB ≈ 1 minute for compressed audio
            minutes = int(size_mb)
            return f"~{minutes} min"
        except:
            return "Unknown"
    
    def generate_summary_tabs_html(self, summaries: List[Dict[str, str]]) -> str:
        """Generate HTML for summary tabs"""
        if not summaries:
            return ""
        
        tabs_html = []
        for summary in summaries:
            tabs_html.append(f'''
                <button class="tab-button" id="btn-{summary['code']}" onclick="switchTab('{summary['code']}')">
                    {summary['name']}
                </button>
            ''')
        
        return '\n'.join(tabs_html)
    
    def generate_summary_contents_html(self, summaries: List[Dict[str, str]]) -> str:
        """Generate HTML for summary content sections"""
        if not summaries:
            return '<p>Ingen sammendrag tilgjengelig</p>'
        
        contents_html = []
        for summary in summaries:
            contents_html.append(f'''
                <div class="tab-content" id="tab-{summary['code']}">
                    <div class="summary-header">
                        <h3>{summary['name']} sammendrag</h3>
                        <div class="edit-controls">
                            <span class="status-message" id="status-{summary['code']}"></span>
                            <button class="btn btn-edit" id="edit-summary-{summary['code']}" 
                                    onclick="enableSummaryEditing('{summary['code']}')">
                                ✏️ Rediger
                            </button>
                            <button class="btn btn-save" id="save-summary-{summary['code']}" 
                                    onclick="saveSummary('{summary['code']}')">
                                💾 Lagre
                            </button>
                            <button class="btn btn-cancel" id="cancel-summary-{summary['code']}" 
                                    onclick="cancelSummaryEditing('{summary['code']}')">
                                ❌ Avbryt
                            </button>
                        </div>
                    </div>
                    
                    <div id="summary-display-{summary['code']}" class="summary-display">
                        <!-- Loaded via JavaScript -->
                    </div>
                    
                    <textarea id="summary-editor-{summary['code']}" class="summary-editor"></textarea>
                </div>
            ''')
        
        return '\n'.join(contents_html)
    
    def generate_html(self, txt_path: Path) -> Optional[Path]:
        """Generate HTML for a single transcription"""
        base_name = txt_path.stem
        parent = txt_path.parent
        
        # Find summaries
        summaries = self.find_summaries(txt_path)
        if not summaries:
            print(f"No summaries found for {base_name}")
            return None
        
        # Find audio file
        audio_path = self.find_audio_file(txt_path)
        
        # Extract date from filename (assumes format: DDMMYY - ...)
        try:
            date_str = base_name.split(' - ')[0]
            if len(date_str) == 6:
                day = date_str[0:2]
                month = date_str[2:4]
                year = date_str[4:6]
                formatted_date = f"{day}.{month}.20{year}"
            else:
                formatted_date = "Unknown Date"
        except:
            formatted_date = "Unknown Date"
        
        # Generate audio player HTML
        if audio_path:
            duration = self.format_duration(audio_path)
            audio_html = f'''
            <div class="audio-player">
                <h3>🎵 Lydfil</h3>
                <audio controls>
                    <source src="{audio_path.name}" type="audio/{audio_path.suffix[1:]}">
                    Din nettleser støtter ikke audio-elementet.
                </audio>
            </div>
            '''
        else:
            duration = "N/A"
            audio_html = ""
        
        # Get contact info
        contact = self.config.get('contact', {})
        contact_name = contact.get('name', 'Unknown')
        contact_phone = contact.get('phone', '')
        contact_github = contact.get('github', '')
        
        # Generate HTML from template
        html = self.template
        html = html.replace('{{TITLE}}', base_name)
        html = html.replace('{{DATE}}', formatted_date)
        html = html.replace('{{DURATION}}', duration)
        html = html.replace('{{AUDIO_PLAYER}}', audio_html)
        html = html.replace('{{SUMMARY_TABS}}', self.generate_summary_tabs_html(summaries))
        html = html.replace('{{SUMMARY_CONTENTS}}', self.generate_summary_contents_html(summaries))
        html = html.replace('{{BASE_NAME}}', base_name)
        html = html.replace('{{AVAILABLE_SUMMARIES}}', json.dumps(summaries))
        html = html.replace('{{CONTACT_NAME}}', contact_name)
        html = html.replace('{{CONTACT_PHONE}}', contact_phone)
        html = html.replace('{{CONTACT_GITHUB}}', contact_github)
        
        # Save HTML file
        html_path = parent / f"{base_name}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated: {html_path}")
        return html_path
    
    def generate_all(self):
        """Generate HTML for all transcriptions"""
        txt_files = self.find_transcription_files()
        
        if not txt_files:
            print("No transcription files found")
            return
        
        print(f"Found {len(txt_files)} transcription files")
        
        generated = []
        for txt_file in txt_files:
            html_path = self.generate_html(txt_file)
            if html_path:
                generated.append(html_path)
        
        print(f"\nGenerated {len(generated)} HTML files")
        return generated


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate HTML with editable summaries and transcripts")
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--file', help='Process specific transcription file')
    
    args = parser.parse_args()
    
    try:
        generator = EditableHTMLGenerator(args.config)
        
        if args.file:
            txt_file = Path(args.file)
            if not txt_file.exists():
                print(f"File not found: {txt_file}")
                sys.exit(1)
            
            generator.generate_html(txt_file)
        else:
            generator.generate_all()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
