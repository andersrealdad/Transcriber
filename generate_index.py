#!/usr/bin/env python3
"""
HTML Index Generator for Transcription System
Creates navigation system with audio players
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Optional
import datetime
import json


class HTMLIndexGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        log_level = getattr(logging, self.config['processing']['log_level'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.input_folder = Path(self.config['folders']['input'])
        self.audio_extensions = [f".{ext}" for ext in self.config['audio']['formats']]
        
        if not self.input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")

    def scan_folders(self) -> Dict:
        """Scan input folder and collect file information"""
        folder_data = {}
        total_files = 0
        
        # Scan recursively for folders containing media files
        for item in self.input_folder.rglob("*"):
            if item.is_file() and item.suffix.lower() in self.audio_extensions:
                folder = item.parent
                rel_folder = folder.relative_to(self.input_folder)
                folder_key = str(rel_folder) if rel_folder != Path(".") else "root"
                
                if folder_key not in folder_data:
                    folder_data[folder_key] = {
                        'path': folder,
                        'rel_path': rel_folder,
                        'files': [],
                        'display_name': folder.name if folder != self.input_folder else "Root"
                    }
                
                # Check for associated files
                stem = item.stem
                file_info = {
                    'audio_file': item,
                    'stem': stem,
                    'has_transcript': (folder / f"{stem}.txt").exists(),
                    'has_summary_no': (folder / f"{stem}_no.md").exists(),
                    'has_summary_en': (folder / f"{stem}_en.md").exists(),
                    'has_html': (folder / f"{stem}.html").exists()
                }
                
                folder_data[folder_key]['files'].append(file_info)
                total_files += 1
        
        return folder_data, total_files

    def generate_all_indexes(self):
        """Generate all HTML indexes"""
        self.logger.info("Generating HTML navigation system...")
        
        folder_data, total_files = self.scan_folders()
        
        # Generate main index
        self.generate_hovedindex(folder_data, total_files)
        
        # Generate folder indexes and individual file pages
        for folder_key, folder_info in folder_data.items():
            self.generate_folder_index(folder_key, folder_info, folder_data)
            
            # Generate individual file pages
            for file_info in folder_info['files']:
                self.generate_file_page(file_info, folder_info, folder_data)
        
        self.logger.info(f"Generated HTML navigation for {len(folder_data)} folders, {total_files} files")

    def generate_hovedindex(self, folder_data: Dict, total_files: int):
        """Generate main index (hovedindex.html)"""
        html_content = self._get_hovedindex_template(folder_data, total_files)
        
        hovedindex_path = self.input_folder / "hovedindex.html"
        with open(hovedindex_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated hovedindex: {hovedindex_path}")

    def generate_folder_index(self, folder_key: str, folder_info: Dict, all_folders: Dict):
        """Generate folder index (folder_index.html)"""
        html_content = self._get_folder_index_template(folder_key, folder_info, all_folders)
        
        folder_index_path = folder_info['path'] / "folder_index.html"
        with open(folder_index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated folder index: {folder_index_path}")

    def generate_file_page(self, file_info: Dict, folder_info: Dict, all_folders: Dict):
        """Generate individual file page with audio player"""
        html_content = self._get_file_page_template(file_info, folder_info, all_folders)
        
        file_page_path = folder_info['path'] / f"{file_info['stem']}.html"
        with open(file_page_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated file page: {file_page_path}")

    def _get_base_styles(self) -> str:
        """Get base CSS styles"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .breadcrumb {
            background: rgba(255, 255, 255, 0.9);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
            margin-right: 10px;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .folder-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        
        .status-missing {
            background: #f8d7da;
            color: #721c24;
        }
        
        .audio-player {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .audio-player audio {
            width: 100%;
            margin: 10px 0;
        }
        
        .transcript-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .transcript-line {
            margin: 8px 0;
            padding: 5px;
            border-radius: 5px;
            transition: background-color 0.2s;
        }
        
        .transcript-line:hover {
            background: rgba(52, 152, 219, 0.1);
        }
        
        .timestamp {
            color: #3498db;
            font-weight: bold;
            cursor: pointer;
            margin-right: 10px;
        }
        
        .timestamp:hover {
            text-decoration: underline;
        }
        
        .summary-tabs {
            margin: 20px 0;
        }
        
        .tab-buttons {
            display: flex;
            border-bottom: 2px solid #e9ecef;
            margin-bottom: 20px;
        }
        
        .tab-button {
            background: none;
            border: none;
            padding: 12px 24px;
            cursor: pointer;
            font-size: 1em;
            color: #6c757d;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab-button.active {
            color: #3498db;
            border-bottom-color: #3498db;
        }
        
        .tab-content {
            display: none;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .download-links {
            background: #e9ecef;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        
        .download-links a {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            margin: 5px;
            transition: background-color 0.3s;
        }
        
        .download-links a:hover {
            background: #2980b9;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 10px;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
        }
        
        .search-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .search-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        .search-results {
            margin-top: 10px;
            color: #6c757d;
            font-size: 14px;
        }
        
        .highlight {
            background-color: #fff3cd;
            color: #856404;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .folder-grid,
            .file-grid {
                grid-template-columns: 1fr;
            }
            
            .tab-buttons {
                flex-direction: column;
            }
        }
        """

    def _get_hovedindex_template(self, folder_data: Dict, total_files: int) -> str:
        """Generate hovedindex.html template"""
        
        # Calculate statistics
        total_transcripts = sum(len([f for f in folder['files'] if f['has_transcript']]) 
                              for folder in folder_data.values())
        total_summaries = sum(len([f for f in folder['files'] if f['has_summary_no'] or f['has_summary_en']]) 
                            for folder in folder_data.values())
        
        # Generate folder cards
        folder_cards = ""
        for folder_key, folder_info in sorted(folder_data.items()):
            file_count = len(folder_info['files'])
            transcript_count = len([f for f in folder_info['files'] if f['has_transcript']])
            summary_count = len([f for f in folder_info['files'] if f['has_summary_no'] or f['has_summary_en']])
            
            folder_link = f"{folder_info['rel_path']}/folder_index.html" if folder_key != "root" else "folder_index.html"
            
            folder_cards += f"""
            <div class="card">
                <h3><a href="{folder_link}" style="text-decoration: none; color: #2c3e50;">
                    📁 {folder_info['display_name']}
                </a></h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">{file_count}</div>
                        <div>Audio Files</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{transcript_count}</div>
                        <div>Transcripts</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{summary_count}</div>
                        <div>Summaries</div>
                    </div>
                </div>
                <p style="margin-top: 15px; color: #7f8c8d;">
                    Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
                </p>
            </div>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎙️ STENOGRAFEN - Audio Archive</title>
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ STENOGRAFEN</h1>
            <p class="subtitle">AI-Powered Audio Transcription Archive</p>
        </div>
        
        <div class="card">
            <h2>📊 Archive Statistics</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(folder_data)}</div>
                    <div>Folders</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_files}</div>
                    <div>Audio Files</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_transcripts}</div>
                    <div>Transcripts</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_summaries}</div>
                    <div>AI Summaries</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📁 Browse Folders</h2>
            <div class="folder-grid">
                {folder_cards}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Powered by Faster-Whisper & Ollama AI</p>
        </div>
    </div>
</body>
</html>"""

    def _get_folder_index_template(self, folder_key: str, folder_info: Dict, all_folders: Dict) -> str:
        """Generate folder_index.html template"""
        
        # Generate breadcrumb
        breadcrumb = '<a href="../hovedindex.html">🏠 Home</a> → 📁 ' + folder_info['display_name']
        
        # Generate file cards
        file_cards = ""
        for file_info in sorted(folder_info['files'], key=lambda x: x['stem']):
            # Status badges
            status_badges = ""
            if file_info['has_transcript']:
                status_badges += '<span class="status-badge status-success">✓ Transcript</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ Transcript</span>'
            
            if file_info['has_summary_no']:
                status_badges += '<span class="status-badge status-success">✓ Summary (NO)</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ Summary (NO)</span>'
            
            if file_info['has_summary_en']:
                status_badges += '<span class="status-badge status-success">✓ Summary (EN)</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ Summary (EN)</span>'
            
            # File size
            try:
                file_size = file_info['audio_file'].stat().st_size
                size_mb = file_size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            except:
                size_str = "Unknown"
            
            file_cards += f"""
            <div class="card">
                <h3><a href="{file_info['stem']}.html" style="text-decoration: none; color: #2c3e50;">
                    🎵 {file_info['stem']}
                </a></h3>
                <p><strong>Format:</strong> {file_info['audio_file'].suffix.upper()} • <strong>Size:</strong> {size_str}</p>
                <div style="margin: 10px 0;">
                    {status_badges}
                </div>
                <p style="margin-top: 15px;">
                    <a href="{file_info['stem']}.html" style="color: #3498db; text-decoration: none;">
                        ▶️ Open Player & Transcript
                    </a>
                </p>
            </div>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📁 {folder_info['display_name']} - STENOGRAFEN</title>
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            {breadcrumb}
        </div>
        
        <div class="header">
            <h1>📁 {folder_info['display_name']}</h1>
            <p class="subtitle">{len(folder_info['files'])} audio files</p>
        </div>
        
        <div class="card">
            <h2>🎵 Audio Files</h2>
            <div class="file-grid">
                {file_cards}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""

    def _get_file_page_template(self, file_info: Dict, folder_info: Dict, all_folders: Dict) -> str:
        """Generate individual file page with audio player"""
        
        # Generate breadcrumb
        if folder_info['rel_path'] == Path("."):
            breadcrumb = '<a href="../hovedindex.html">🏠 Home</a> → <a href="folder_index.html">📁 Root</a> → 🎵 ' + file_info['stem']
            folder_link = "folder_index.html"
            home_link = "hovedindex.html"
        else:
            breadcrumb = f'<a href="../hovedindex.html">🏠 Home</a> → <a href="folder_index.html">📁 {folder_info["display_name"]}</a> → 🎵 {file_info["stem"]}'
            folder_link = "folder_index.html"
            home_link = "../hovedindex.html"
        
        # Load transcript
        transcript_content = ""
        if file_info['has_transcript']:
            try:
                transcript_path = folder_info['path'] / f"{file_info['stem']}.txt"
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_lines = f.readlines()
                
                for line in transcript_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse timestamp
                    import re
                    timestamp_match = re.match(r'\[(\d{2}):(\d{2}):(\d{2})\](.+)', line)
                    if timestamp_match:
                        h, m, s, text = timestamp_match.groups()
                        total_seconds = int(h) * 3600 + int(m) * 60 + int(s)
                        timestamp_str = f"{h}:{m}:{s}"
                        transcript_content += f"""
                        <div class="transcript-line">
                            <span class="timestamp" onclick="seekAudio({total_seconds})">[{timestamp_str}]</span>
                            <span class="text">{text.strip()}</span>
                        </div>
                        """
                    else:
                        transcript_content += f'<div class="transcript-line"><span class="text">{line}</span></div>'
            except Exception as e:
                transcript_content = f"<p>Error loading transcript: {e}</p>"
        else:
            transcript_content = "<p>No transcript available</p>"
        
        # Add search section
        search_section = """
        <div class="search-section">
            <h3>🔍 Search Transcript</h3>
            <input type="text" id="searchInput" placeholder="Search for words in transcript..." class="search-input">
            <div id="searchResults" class="search-results"></div>
        </div>
        """
        
        transcript_content_with_search = f"{search_section}{transcript_content}"
        
        # Load summaries
        summary_tabs = ""
        summary_content = ""
        
        if file_info['has_summary_no'] or file_info['has_summary_en']:
            summary_tabs = '<div class="tab-buttons">'
            
            if file_info['has_summary_no']:
                summary_tabs += '<button class="tab-button active" onclick="showTab(\'no\')">🇳🇴 Norwegian</button>'
                
                try:
                    summary_path = folder_info['path'] / f"{file_info['stem']}_no.md"
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary_no = f.read()
                    
                    summary_content += f"""
                    <div id="tab-no" class="tab-content active">
                        <div style="white-space: pre-wrap; font-family: inherit;">{summary_no}</div>
                    </div>
                    """
                except Exception as e:
                    summary_content += f'<div id="tab-no" class="tab-content active"><p>Error loading Norwegian summary: {e}</p></div>'
            
            if file_info['has_summary_en']:
                active_class = "" if file_info['has_summary_no'] else "active"
                summary_tabs += f'<button class="tab-button {active_class}" onclick="showTab(\'en\')">🇬🇧 English</button>'
                
                try:
                    summary_path = folder_info['path'] / f"{file_info['stem']}_en.md"
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary_en = f.read()
                    
                    active_class = "" if file_info['has_summary_no'] else "active"
                    summary_content += f"""
                    <div id="tab-en" class="tab-content {active_class}">
                        <div style="white-space: pre-wrap; font-family: inherit;">{summary_en}</div>
                    </div>
                    """
                except Exception as e:
                    summary_content += f'<div id="tab-en" class="tab-content {active_class}"><p>Error loading English summary: {e}</p></div>'
            
            summary_tabs += '</div>'
        
        # Generate download links
        download_links = ""
        if file_info['has_transcript']:
            download_links += f'<a href="{file_info["stem"]}.txt" download>📄 Download Transcript</a>'
        if file_info['has_summary_no']:
            download_links += f'<a href="{file_info["stem"]}_no.md" download>📋 Download Summary (NO)</a>'
        if file_info['has_summary_en']:
            download_links += f'<a href="{file_info["stem"]}_en.md" download>📋 Download Summary (EN)</a>'
        
        # Audio player
        audio_player = f"""
        <div class="audio-player">
            <h3>🎵 Audio Player</h3>
            <audio id="audioPlayer" controls preload="metadata">
                <source src="{file_info['audio_file'].name}" type="audio/{file_info['audio_file'].suffix[1:]}">
                Your browser does not support the audio element.
            </audio>
            <p><strong>File:</strong> {file_info['audio_file'].name}</p>
        </div>
        """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 {file_info['stem']} - STENOGRAFEN</title>
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            {breadcrumb}
        </div>
        
        <div class="header">
            <h1>🎵 {file_info['stem']}</h1>
            <p class="subtitle">Audio Player & Transcript</p>
        </div>
        
        {audio_player}
        
        <div class="card">
            <h2>📝 Transcript</h2>
            <div class="transcript-section">
                {transcript_content_with_search}
            </div>
        </div>
        
        {f'''
        <div class="card">
            <h2>📋 AI Summaries</h2>
            <div class="summary-tabs">
                {summary_tabs}
                {summary_content}
            </div>
        </div>
        ''' if file_info['has_summary_no'] or file_info['has_summary_en'] else ''}
        
        <div class="card">
            <h2>💾 Downloads</h2>
            <div class="download-links">
                {download_links}
            </div>
        </div>
        
        <div class="footer">
            <p>
                <a href="{folder_link}">← Back to Folder</a> • 
                <a href="{home_link}">🏠 Home</a>
            </p>
            <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function seekAudio(seconds) {{
            const audio = document.getElementById('audioPlayer');
            audio.currentTime = seconds;
            audio.play();
        }}
        
        function showTab(tabId) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Search functionality
        let originalTranscript = '';
        
        document.addEventListener('DOMContentLoaded', function() {{
            const transcriptContent = document.querySelector('.transcript-section');
            const searchInput = document.getElementById('searchInput');
            const searchResults = document.getElementById('searchResults');
            
            if (transcriptContent) {{
                // Store original content (excluding search section)
                const transcriptLines = transcriptContent.querySelectorAll('.transcript-line');
                originalTranscript = Array.from(transcriptLines).map(line => line.outerHTML).join('');
            }}
            
            if (searchInput) {{
                searchInput.addEventListener('input', function() {{
                    const query = this.value.trim();
                    performSearch(query);
                }});
            }}
        }});
        
        function performSearch(query) {{
            const transcriptSection = document.querySelector('.transcript-section');
            const searchResults = document.getElementById('searchResults');
            const transcriptLines = transcriptSection.querySelectorAll('.transcript-line');
            
            if (!query) {{
                // Restore original content
                transcriptLines.forEach(line => {{
                    line.innerHTML = line.innerHTML.replace(/<span class="highlight">(.*?)<\/span>/g, '$1');
                }});
                searchResults.textContent = '';
                return;
            }}
            
            // Remove previous highlights
            transcriptLines.forEach(line => {{
                line.innerHTML = line.innerHTML.replace(/<span class="highlight">(.*?)<\/span>/g, '$1');
            }});
            
            // Escape special regex characters
            const escapedQuery = query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
            const regex = new RegExp(`(${{escapedQuery}})`, 'gi');
            
            let matchCount = 0;
            
            // Highlight matches in each line
            transcriptLines.forEach(line => {{
                const textSpan = line.querySelector('.text');
                if (textSpan) {{
                    const originalText = textSpan.textContent;
                    const matches = originalText.match(regex);
                    if (matches) {{
                        matchCount += matches.length;
                        const highlightedText = originalText.replace(regex, '<span class="highlight">$1</span>');
                        textSpan.innerHTML = highlightedText;
                    }}
                }}
            }});
            
            // Update results
            if (matchCount > 0) {{
                searchResults.textContent = `Found ${{matchCount}} match${{matchCount !== 1 ? 'es' : ''}}`;
            }} else {{
                searchResults.textContent = 'No matches found';
            }}
        }}
        
        // Update transcript highlighting based on audio position
        const audio = document.getElementById('audioPlayer');
        if (audio) {{
            audio.addEventListener('timeupdate', function() {{
                const currentTime = Math.floor(audio.currentTime);
                
                // Remove previous highlights
                document.querySelectorAll('.transcript-line').forEach(line => {{
                    line.style.backgroundColor = '';
                }});
                
                // Find and highlight current line
                const timestamps = document.querySelectorAll('.timestamp');
                for (let i = 0; i < timestamps.length; i++) {{
                    const timestamp = timestamps[i];
                    const onclick = timestamp.getAttribute('onclick');
                    const match = onclick.match(/seekAudio\\\\((\\\\d+)\\\\)/);
                    if (match) {{
                        const lineTime = parseInt(match[1]);
                        const nextLineTime = i < timestamps.length - 1 ? 
                            parseInt(timestamps[i + 1].getAttribute('onclick').match(/seekAudio\\\\((\\\\d+)\\\\)/)[1]) : 
                            Infinity;
                        
                        if (currentTime >= lineTime && currentTime < nextLineTime) {{
                            timestamp.parentElement.style.backgroundColor = 'rgba(52, 152, 219, 0.2)';
                            break;
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate HTML navigation system")
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        generator = HTMLIndexGenerator(args.config)
        generator.generate_all_indexes()
        print("✅ HTML navigation system generated successfully!")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
