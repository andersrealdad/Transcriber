#!/usr/bin/env python3
"""
Enhanced HTML Index Generator for Transcription System
Supports dual themes: Nostalgia (hacker) and Modern (professional)
Creates navigation with audio players, clickable timestamps, and dual-language summaries
"""

import os
import sys
import yaml
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
import datetime


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
        
        # Get theme from config (default to 'modern')
        self.theme = self.config.get('html_generation', {}).get('theme', 'modern')
        self.current_theme = None  # Will be set during generation
        
        if not self.input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")
        
        self.logger.info(f"Using theme: {self.theme}")

    def parse_timestamp_to_seconds(self, timestamp: str) -> int:
        """Convert [HH:MM:SS] or [MM:SS] timestamp to seconds"""
        timestamp = timestamp.strip('[]')
        parts = timestamp.split(':')
        
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return 0

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
                    'transcript_path': folder / f"{stem}.txt",
                    'summary_no_path': folder / f"{stem}_no.md",
                    'summary_en_path': folder / f"{stem}_en.md",
                }
                
                folder_data[folder_key]['files'].append(file_info)
                total_files += 1
        
        return folder_data, total_files

    def generate_all_indexes(self, generate_both_themes: bool = False):
        """Generate all HTML indexes"""
        self.logger.info("Generating HTML navigation system...")
        
        folder_data, total_files = self.scan_folders()
        
        if generate_both_themes:
            # Generate both themes
            self.logger.info("Generating BOTH themes...")
            
            # Generate Nostalgia theme
            self.current_theme = 'nostalgia'
            self.logger.info("Generating Nostalgia theme...")
            for folder_key, folder_info in folder_data.items():
                self.generate_folder_index(folder_key, folder_info, folder_data)
                for file_info in folder_info['files']:
                    self.generate_file_page(file_info, folder_info, folder_data)
            
            # Generate Modern theme
            self.current_theme = 'modern'
            self.logger.info("Generating Modern theme...")
            for folder_key, folder_info in folder_data.items():
                self.generate_folder_index(folder_key, folder_info, folder_data)
                for file_info in folder_info['files']:
                    self.generate_file_page(file_info, folder_info, folder_data)
            
            # Generate unified hovedindex with theme chooser
            self.generate_unified_hovedindex(folder_data, total_files)
        else:
            # Generate single theme
            self.current_theme = self.theme
            self.generate_hovedindex(folder_data, total_files)
            
            for folder_key, folder_info in folder_data.items():
                self.generate_folder_index(folder_key, folder_info, folder_data)
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

    def generate_unified_hovedindex(self, folder_data: Dict, total_files: int):
        """Generate unified hoofdindex with theme chooser for both themes"""
        html_content = self._get_unified_hovedindex_template(folder_data, total_files)
        
        hovedindex_path = self.input_folder / "hovedindex.html"
        with open(hovedindex_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated unified hovedindex with theme chooser: {hovedindex_path}")

    def generate_folder_index(self, folder_key: str, folder_info: Dict, all_folders: Dict):
        """Generate folder index (folder_index.html)"""
        html_content = self._get_folder_index_template(folder_key, folder_info, all_folders)
        
        # Add theme suffix to filename
        theme_suffix = '-n' if self.current_theme == 'nostalgia' else '-m'
        folder_index_path = folder_info['path'] / f"folder_index{theme_suffix}.html"
        with open(folder_index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated folder index: {folder_index_path}")

    def generate_file_page(self, file_info: Dict, folder_info: Dict, all_folders: Dict):
        """Generate individual file page with audio player"""
        html_content = self._get_file_page_template(file_info, folder_info, all_folders)
        
        # Add theme suffix to filename
        theme_suffix = '-n' if self.current_theme == 'nostalgia' else '-m'
        file_page_path = folder_info['path'] / f"{file_info['stem']}{theme_suffix}.html"
        with open(file_page_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated file page: {file_page_path}")

    def _get_nostalgia_styles(self) -> str:
        """Get Nostalgia (hacker/terminal) theme CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background-color: #0a0a0a;
            color: #00ff00;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background-color: #1a1a1a;
            padding: 30px;
            border: 2px solid #00ff00;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        
        .header h1 {
            color: #00ff00;
            font-size: 2em;
            text-shadow: 0 0 10px #00ff00;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #00ffff;
            font-size: 1em;
            text-shadow: 0 0 5px #00ffff;
        }
        
        .header pre {
            margin: 20px 0;
            font-size: 8px;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .breadcrumb {
            background-color: #1a1a1a;
            border: 1px solid #333;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        .breadcrumb a {
            color: #00ff00;
            text-decoration: none;
            margin-right: 10px;
            transition: color 0.3s;
        }
        
        .breadcrumb a:hover {
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }
        
        .card {
            background-color: #1a1a1a;
            border: 1px solid #333;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 5px;
            transition: border-color 0.3s;
        }
        
        .card:hover {
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
        }
        
        .card h2, .card h3 {
            color: #00ffff;
            margin-bottom: 15px;
            text-shadow: 0 0 5px #00ffff;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        
        .folder-grid, .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
            border: 1px solid;
        }
        
        .status-success {
            background: #1a3a1a;
            color: #00ff00;
            border-color: #00ff00;
        }
        
        .status-missing {
            background: #3a1a1a;
            color: #ff0000;
            border-color: #ff0000;
        }
        
        .audio-player {
            background-color: #2a2a2a;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .audio-player h3 {
            color: #00ffff;
            margin-bottom: 10px;
        }
        
        .audio-player audio {
            width: 100%;
            margin: 10px 0;
            background-color: #1a1a1a;
        }
        
        .transcript-section {
            background-color: #0f0f0f;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .transcript-section::-webkit-scrollbar {
            width: 10px;
        }
        
        .transcript-section::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        
        .transcript-section::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 5px;
        }
        
        .transcript-line {
            margin: 8px 0;
            padding: 8px;
            border-left: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .transcript-line:hover {
            background-color: rgba(0, 255, 0, 0.1);
            border-left-color: #00ff00;
        }
        
        .transcript-line.current {
            background-color: rgba(0, 255, 255, 0.2);
            border-left-color: #00ffff;
        }
        
        .timestamp {
            color: #00ffff;
            font-weight: bold;
            cursor: pointer;
            margin-right: 10px;
            text-shadow: 0 0 3px #00ffff;
        }
        
        .timestamp:hover {
            color: #00ff00;
            text-decoration: underline;
        }
        
        .text {
            color: #00ff00;
        }
        
        .search-box {
            background-color: #2a2a2a;
            border: 1px solid #00ff00;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        
        .search-box input {
            width: 100%;
            padding: 10px;
            background-color: #1a1a1a;
            border: 1px solid #333;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            border-radius: 3px;
        }
        
        .search-box input::placeholder {
            color: #666;
        }
        
        .search-results {
            color: #00ffff;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .highlight {
            background-color: rgba(255, 255, 0, 0.3);
            color: #ffff00;
            padding: 2px;
        }
        
        .summary-tabs {
            margin: 20px 0;
        }
        
        .tab-buttons {
            display: flex;
            border-bottom: 2px solid #333;
            margin-bottom: 20px;
        }
        
        .tab-button {
            background: #1a1a1a;
            border: 1px solid #333;
            border-bottom: none;
            padding: 12px 24px;
            cursor: pointer;
            font-size: 1em;
            font-family: 'Courier New', monospace;
            color: #00ff00;
            transition: all 0.3s ease;
            margin-right: 5px;
        }
        
        .tab-button:hover {
            background: #2a2a2a;
        }
        
        .tab-button.active {
            color: #00ffff;
            border-color: #00ff00;
            background: #2a2a2a;
            text-shadow: 0 0 5px #00ffff;
        }
        
        .tab-content {
            display: none;
            background-color: #0f0f0f;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 20px;
            color: #00ff00;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .tab-content pre {
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }
        
        .download-links {
            background-color: #2a2a2a;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        
        .download-links a {
            display: inline-block;
            background-color: #1a3a1a;
            color: #00ff00;
            padding: 10px 20px;
            border: 1px solid #00ff00;
            border-radius: 3px;
            text-decoration: none;
            margin: 5px;
            transition: all 0.3s;
            font-weight: bold;
        }
        
        .download-links a:hover {
            background-color: #00ff00;
            color: #000;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 5px;
            transition: border-color 0.3s;
        }
        
        .stat-item:hover {
            border-color: #00ff00;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            display: block;
        }
        
        .stat-label {
            color: #00ff00;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .footer {
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #333;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        
        .footer a {
            color: #00ff00;
            text-decoration: none;
            margin: 0 10px;
        }
        
        .footer a:hover {
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }
        
        a {
            color: #00ff00;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        a:hover {
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header pre {
                font-size: 6px;
            }
            
            .folder-grid, .file-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.5em;
            }
        }
        """

    def _get_modern_styles(self) -> str:
        """Get Modern (professional) theme CSS"""
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
        
        .card h2, .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
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
        
        .audio-player h3 {
            color: #2c3e50;
            margin-bottom: 10px;
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
            max-height: 600px;
            overflow-y: auto;
        }
        
        .transcript-section::-webkit-scrollbar {
            width: 10px;
        }
        
        .transcript-section::-webkit-scrollbar-track {
            background: #e9ecef;
        }
        
        .transcript-section::-webkit-scrollbar-thumb {
            background: #3498db;
            border-radius: 5px;
        }
        
        .transcript-line {
            margin: 8px 0;
            padding: 8px;
            border-radius: 5px;
            transition: background-color 0.2s;
        }
        
        .transcript-line:hover {
            background: rgba(52, 152, 219, 0.1);
        }
        
        .transcript-line.current {
            background: rgba(52, 152, 219, 0.2);
            border-left: 3px solid #3498db;
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
        
        .text {
            color: #2c3e50;
        }
        
        .search-box {
            background: #fff;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .search-box input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .search-results {
            color: #7f8c8d;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .highlight {
            background-color: #fff176;
            padding: 2px;
            border-radius: 2px;
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
        
        .tab-button:hover {
            color: #2c3e50;
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
        
        .tab-content pre {
            white-space: pre-wrap;
            font-family: inherit;
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
            padding: 10px 20px;
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
            padding: 20px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 10px;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
            display: block;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .footer {
            margin-top: 40px;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .footer a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            margin: 0 10px;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .folder-grid, .file-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
        """

    def _get_theme_styles(self) -> str:
        """Get CSS styles based on theme selection"""
        theme = self.current_theme if self.current_theme else self.theme
        if theme == 'nostalgia':
            return self._get_nostalgia_styles()
        else:
            return self._get_modern_styles()

    def _get_ascii_logo(self) -> str:
        """Get ASCII logo for nostalgia theme"""
        return """
   _____ _______ ______ _   _  ____   _____ _____            ______ ______ _   _ 
  / ____|__   __|  ____| \\ | |/ __ \\ / ____|  __ \\     /\\   |  ____|  ____| \\ | |
 | (___    | |  | |__  |  \\| | |  | | |  __| |__) |   /  \\  | |__  | |__  |  \\| |
  \\___ \\   | |  |  __| | . ` | |  | | | |_ |  _  /   / /\\ \\ |  __| |  __| | . ` |
  ____) |  | |  | |____| |\\  | |__| | |__| | | \\ \\  / ____ \\| |    | |____| |\\  |
 |_____/   |_|  |______|_| \\_|\\____/ \\_____|_|  \\_\\/_/    \\_\\_|    |______|_| \\_|
        """

    def _get_hovedindex_template(self, folder_data: Dict, total_files: int) -> str:
        """Generate main index HTML"""
        # Count statistics
        total_folders = len(folder_data)
        transcribed = sum(1 for f in folder_data.values() for file in f['files'] if file['has_transcript'])
        summarized_no = sum(1 for f in folder_data.values() for file in f['files'] if file['has_summary_no'])
        summarized_en = sum(1 for f in folder_data.values() for file in f['files'] if file['has_summary_en'])
        
        # Build folder cards
        folder_cards = ""
        for folder_key, folder_info in sorted(folder_data.items()):
            file_count = len(folder_info['files'])
            folder_link = str(folder_info['rel_path'] / 'folder_index.html') if folder_key != 'root' else 'folder_index.html'
            
            status_badges = ""
            for file in folder_info['files']:
                if file['has_transcript']:
                    status_badges += '<span class="status-badge status-success">✓ Transcript</span>'
                if file['has_summary_no']:
                    status_badges += '<span class="status-badge status-success">✓ NO</span>'
                if file['has_summary_en']:
                    status_badges += '<span class="status-badge status-success">✓ EN</span>'
                break  # Just show first file status
            
            folder_cards += f"""
            <div class="card">
                <h3>📁 {folder_info['display_name']}</h3>
                <p><strong>Files:</strong> {file_count}</p>
                <p>{status_badges}</p>
                <p><a href="{folder_link}">View Folder →</a></p>
            </div>
            """
        
        # Build header based on theme
        if self.theme == 'nostalgia':
            header_content = f"""
            <pre>{self._get_ascii_logo()}</pre>
            <div class="subtitle">Legal Transcription System</div>
            """
        else:
            header_content = """
            <h1>STENOGRAFEN</h1>
            <p class="subtitle">Legal Transcription System</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STENOGRAFEN - Main Index</title>
    <style>{self._get_theme_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            {header_content}
        </div>
        
        <div class="card">
            <h2>📊 Statistics</h2>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{total_folders}</span>
                    <span class="stat-label">Folders</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_files}</span>
                    <span class="stat-label">Audio Files</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{transcribed}</span>
                    <span class="stat-label">Transcribed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{summarized_no}</span>
                    <span class="stat-label">Norwegian Summaries</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{summarized_en}</span>
                    <span class="stat-label">English Summaries</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📁 Folders ({total_folders})</h2>
            <div class="folder-grid">
                {folder_cards}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Theme: {self.theme.capitalize()}</p>
        </div>
    </div>
</body>
</html>"""

    def _get_unified_hovedindex_template(self, folder_data: Dict, total_files: int) -> str:
        """Generate unified hovedindex with theme chooser for both themes"""
        # Count statistics
        total_folders = len(folder_data)
        transcribed = sum(1 for f in folder_data.values() for file in f['files'] if file['has_transcript'])
        summarized_no = sum(1 for f in folder_data.values() for file in f['files'] if file['has_summary_no'])
        summarized_en = sum(1 for f in folder_data.values() for file in f['files'] if file['has_summary_en'])
        
        # Build folder cards for BOTH themes
        folder_cards_nostalgia = ""
        folder_cards_modern = ""
        
        for folder_key, folder_info in sorted(folder_data.items()):
            file_count = len(folder_info['files'])
            folder_link_n = str(folder_info['rel_path'] / 'folder_index-n.html') if folder_key != 'root' else 'folder_index-n.html'
            folder_link_m = str(folder_info['rel_path'] / 'folder_index-m.html') if folder_key != 'root' else 'folder_index-m.html'
            
            status_badges = ""
            for file in folder_info['files']:
                if file['has_transcript']:
                    status_badges += '<span class="status-badge status-success">✓ Transcript</span>'
                if file['has_summary_no']:
                    status_badges += '<span class="status-badge status-success">✓ NO</span>'
                if file['has_summary_en']:
                    status_badges += '<span class="status-badge status-success">✓ EN</span>'
                break  # Just show first file status
            
            folder_cards_nostalgia += f"""
            <div class="card">
                <h3>📁 {folder_info['display_name']}</h3>
                <p><strong>Files:</strong> {file_count}</p>
                <p>{status_badges}</p>
                <p><a href="{folder_link_n}">View Folder →</a></p>
            </div>
            """
            
            folder_cards_modern += f"""
            <div class="card">
                <h3>📁 {folder_info['display_name']}</h3>
                <p><strong>Files:</strong> {file_count}</p>
                <p>{status_badges}</p>
                <p><a href="{folder_link_m}">View Folder →</a></p>
            </div>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STENOGRAFEN - Main Index</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .welcome-header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            text-align: center;
        }}
        
        .welcome-header h1 {{
            color: #2c3e50;
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .welcome-header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        
        .theme-chooser {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }}
        
        .theme-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            font-weight: 600;
            min-width: 250px;
        }}
        
        .theme-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .theme-button.nostalgia {{
            background: linear-gradient(135deg, #0f0f0f 0%, #1a3a1a 100%);
            border: 2px solid #00ff00;
        }}
        
        .theme-button.modern {{
            background: linear-gradient(135deg, #3498db 0%, #2ecc71 100%);
        }}
        
        .theme-view {{
            display: none;
        }}
        
        .theme-view.active {{
            display: block;
        }}
        
        .back-to-chooser {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .back-to-chooser button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 30px;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        
        .back-to-chooser button:hover {{
            background: #2980b9;
        }}
        
        /* Nostalgia Theme Styles */
        .nostalgia-content {{
            font-family: 'Courier New', monospace;
            background-color: #0a0a0a;
            color: #00ff00;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .nostalgia-content .header {{
            background-color: #1a1a1a;
            padding: 30px;
            border: 2px solid #00ff00;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }}
        
        .nostalgia-content .header pre {{
            margin: 0;
            font-size: 8px;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }}
        
        .nostalgia-content .header .subtitle {{
            color: #00ffff;
            font-size: 1em;
            text-shadow: 0 0 5px #00ffff;
            margin-top: 10px;
        }}
        
        .nostalgia-content .card {{
            background-color: #1a1a1a;
            border: 1px solid #333;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 5px;
            transition: border-color 0.3s;
        }}
        
        .nostalgia-content .card:hover {{
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
        }}
        
        .nostalgia-content .card h2, .nostalgia-content .card h3 {{
            color: #00ffff;
            margin-bottom: 15px;
            text-shadow: 0 0 5px #00ffff;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }}
        
        .nostalgia-content .folder-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .nostalgia-content .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .nostalgia-content .stat-item {{
            text-align: center;
            padding: 20px;
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 5px;
            transition: border-color 0.3s;
        }}
        
        .nostalgia-content .stat-item:hover {{
            border-color: #00ff00;
        }}
        
        .nostalgia-content .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            display: block;
        }}
        
        .nostalgia-content .stat-label {{
            color: #00ff00;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .nostalgia-content .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
            border: 1px solid;
        }}
        
        .nostalgia-content .status-success {{
            background: #1a3a1a;
            color: #00ff00;
            border-color: #00ff00;
        }}
        
        .nostalgia-content a {{
            color: #00ff00;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .nostalgia-content a:hover {{
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }}
        
        /* Modern Theme Styles */
        .modern-content {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .modern-content .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .modern-content .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .modern-content .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .modern-content .card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .modern-content .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .modern-content .card h2, .modern-content .card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .modern-content .folder-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .modern-content .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .modern-content .stat-item {{
            text-align: center;
            padding: 20px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 10px;
        }}
        
        .modern-content .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
            display: block;
        }}
        
        .modern-content .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .modern-content .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }}
        
        .modern-content .status-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .modern-content a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .modern-content a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            margin-top: 40px;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
        }}
        
        @media (max-width: 768px) {{
            .welcome-header h1 {{
                font-size: 2em;
            }}
            
            .theme-button {{
                min-width: 200px;
                padding: 15px 30px;
            }}
            
            .folder-grid {{
                grid-template-columns: 1fr !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Theme Chooser -->
        <div id="theme-chooser" class="theme-view active">
            <div class="welcome-header">
                <h1>STENOGRAFEN</h1>
                <p class="subtitle">Legal Transcription System</p>
                <p style="color: #95a5a6; margin-top: 20px;">Choose your viewing experience</p>
                
                <div class="theme-chooser">
                    <button class="theme-button nostalgia" onclick="showTheme('nostalgia')">
                        🖥️ NOSTALGIA<br>
                        <small style="font-weight: normal; font-size: 0.8em;">Terminal / Hacker Style</small>
                    </button>
                    <button class="theme-button modern" onclick="showTheme('modern')">
                        🎯 MODERN<br>
                        <small style="font-weight: normal; font-size: 0.8em;">Professional / Client-Ready</small>
                    </button>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Both themes available • {total_files} files • {total_folders} folders</p>
            </div>
        </div>
        
        <!-- Nostalgia Theme View -->
        <div id="nostalgia-view" class="theme-view">
            <div class="back-to-chooser">
                <button onclick="showTheme('chooser')">← Choose Different Theme</button>
            </div>
            
            <div class="nostalgia-content">
                <div class="header">
                    <pre>{self._get_ascii_logo()}</pre>
                    <div class="subtitle">Legal Transcription System</div>
                </div>
                
                <div class="card">
                    <h2>📊 Statistics</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number">{total_folders}</span>
                            <span class="stat-label">Folders</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{total_files}</span>
                            <span class="stat-label">Audio Files</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{transcribed}</span>
                            <span class="stat-label">Transcribed</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{summarized_no}</span>
                            <span class="stat-label">Norwegian Summaries</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{summarized_en}</span>
                            <span class="stat-label">English Summaries</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📁 Folders ({total_folders})</h2>
                    <div style="margin-bottom: 20px;">
                        <a href="/upload-ui/" class="btn" style="display: inline-block; background: #2ecc71; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                            📤 Upload Files / Create Folder
                        </a>
                    </div>
                    <div class="folder-grid">
                        {folder_cards_nostalgia}
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Nostalgia Theme</p>
            </div>
        </div>
        
        <!-- Modern Theme View -->
        <div id="modern-view" class="theme-view">
            <div class="back-to-chooser">
                <button onclick="showTheme('chooser')">← Choose Different Theme</button>
            </div>
            
            <div class="modern-content">
                <div class="header">
                    <h1>STENOGRAFEN</h1>
                    <p class="subtitle">Legal Transcription System</p>
                </div>
                
                <div class="card">
                    <h2>📊 Statistics</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number">{total_folders}</span>
                            <span class="stat-label">Folders</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{total_files}</span>
                            <span class="stat-label">Audio Files</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{transcribed}</span>
                            <span class="stat-label">Transcribed</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{summarized_no}</span>
                            <span class="stat-label">Norwegian Summaries</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{summarized_en}</span>
                            <span class="stat-label">English Summaries</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📁 Folders ({total_folders})</h2>
                    <div style="margin-bottom: 20px;">
                        <a href="/upload-ui/" class="btn" style="display: inline-block; background: #2ecc71; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                            📤 Upload Files / Create Folder
                        </a>
                    </div>
                    <div class="folder-grid">
                        {folder_cards_modern}
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Modern Theme</p>
            </div>
        </div>
    </div>
    
    <script>
        function showTheme(themeName) {{
            // Hide all views
            document.querySelectorAll('.theme-view').forEach(view => {{
                view.classList.remove('active');
            }});
            
            // Show selected view
            if (themeName === 'chooser') {{
                document.getElementById('theme-chooser').classList.add('active');
            }} else if (themeName === 'nostalgia') {{
                document.getElementById('nostalgia-view').classList.add('active');
            }} else if (themeName === 'modern') {{
                document.getElementById('modern-view').classList.add('active');
            }}
            
            // Scroll to top
            window.scrollTo(0, 0);
        }}
    </script>
</body>
</html>"""

    def _get_folder_index_template(self, folder_key: str, folder_info: Dict, all_folders: Dict) -> str:
        """Generate folder index HTML"""
        # Build breadcrumb
        breadcrumb = '<a href="../hovedindex.html">🏠 Home</a>'
        if folder_key != 'root':
            parts = folder_info['rel_path'].parts
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    breadcrumb += f' / <strong>{part}</strong>'
                else:
                    breadcrumb += f' / {part}'
        
        # Build file cards
        theme_suffix = '-n' if self.current_theme == 'nostalgia' else '-m'
        file_cards = ""
        for file in folder_info['files']:
            status_badges = ""
            if file['has_transcript']:
                status_badges += '<span class="status-badge status-success">✓ Transcript</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ Transcript</span>'
            
            if file['has_summary_no']:
                status_badges += '<span class="status-badge status-success">✓ NO</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ NO</span>'
                
            if file['has_summary_en']:
                status_badges += '<span class="status-badge status-success">✓ EN</span>'
            else:
                status_badges += '<span class="status-badge status-missing">✗ EN</span>'
            
            file_link = f"{file['stem']}{theme_suffix}.html"
            
            file_cards += f"""
            <div class="card">
                <h3>🎵 {file['stem']}</h3>
                <p><strong>Audio:</strong> {file['audio_file'].name}</p>
                <p>{status_badges}</p>
                <p><a href="{file_link}">View Details →</a></p>
            </div>
            """
        
        # Build header based on theme
        if self.current_theme == 'nostalgia':
            header_content = f"""
            <pre style="font-size: 6px;">{self._get_ascii_logo()}</pre>
            <div class="subtitle">📁 {folder_info['display_name']}</div>
            """
        else:
            header_content = f"""
            <h1>📁 {folder_info['display_name']}</h1>
            <p class="subtitle">Folder Index</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📁 {folder_info['display_name']} - STENOGRAFEN</title>
    <style>{self._get_theme_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            {breadcrumb}
        </div>
        
        <div class="header">
            {header_content}
        </div>
        
        <div class="card">
            <h2>🎵 Audio Files ({len(folder_info['files'])})</h2>
            <div class="file-grid">
                {file_cards}
            </div>
        </div>
        
        <div class="footer">
            <p>
                <a href="../hovedindex.html">🏠 Home</a>
            </p>
            <p>Generated by STENOGRAFEN • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""

    def _get_file_page_template(self, file_info: Dict, folder_info: Dict, all_folders: Dict) -> str:
        """Generate individual file page HTML with clickable timestamps and dual summaries"""
        # Build breadcrumb with theme suffix
        theme_suffix = '-n' if self.current_theme == 'nostalgia' else '-m'
        folder_link = f'folder_index{theme_suffix}.html'
        home_link = '../hovedindex.html' if folder_info['path'] != self.input_folder else 'hovedindex.html'
        
        breadcrumb = f'<a href="{home_link}">🏠 Home</a>'
        if folder_info['path'] != self.input_folder:
            breadcrumb += f' / <a href="{folder_link}">📁 {folder_info["display_name"]}</a>'
        breadcrumb += f' / <strong>🎵 {file_info["stem"]}</strong>'
        
        # Parse transcript with clickable timestamps
        transcript_content = ""
        if file_info['has_transcript']:
            try:
                with open(file_info['transcript_path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Match [HH:MM:SS] or [MM:SS] timestamp pattern
                    match = re.match(r'\[(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})\]\s*(.*)', line)
                    if match:
                        timestamp_str = match.group(1)
                        text = match.group(2)
                        seconds = self.parse_timestamp_to_seconds(timestamp_str)
                        
                        transcript_content += f'''
                        <div class="transcript-line" data-time="{seconds}">
                            <span class="timestamp" onclick="seekAudio({seconds})">[{timestamp_str}]</span>
                            <span class="text">{text}</span>
                        </div>
                        '''
            except Exception as e:
                self.logger.error(f"Error reading transcript: {e}")
                transcript_content = '<p>Error loading transcript</p>'
        else:
            transcript_content = '<p>No transcript available</p>'
        
        # Add search box
        transcript_with_search = f"""
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 Search transcript...">
            <div class="search-results" id="searchResults"></div>
        </div>
        {transcript_content}
        """
        
        # Build summary tabs
        summary_tabs = ""
        summary_content = ""
        
        if file_info['has_summary_no'] or file_info['has_summary_en']:
            # Tab buttons
            summary_tabs = '<div class="tab-buttons">'
            
            if file_info['has_summary_no']:
                summary_tabs += '<button class="tab-button active" onclick="showTab(\'no\')">🇳🇴 Norwegian</button>'
            
            if file_info['has_summary_en']:
                active_class = '' if file_info['has_summary_no'] else 'active'
                summary_tabs += f'<button class="tab-button {active_class}" onclick="showTab(\'en\')">🇬🇧 English</button>'
            
            summary_tabs += '</div>'
            
            # Tab content - Norwegian
            if file_info['has_summary_no']:
                try:
                    with open(file_info['summary_no_path'], 'r', encoding='utf-8') as f:
                        summary_no = f.read()
                    summary_content += f'''
                    <div id="tab-no" class="tab-content active">
                        <pre>{summary_no}</pre>
                    </div>
                    '''
                except Exception as e:
                    self.logger.error(f"Error reading Norwegian summary: {e}")
            
            # Tab content - English
            if file_info['has_summary_en']:
                try:
                    with open(file_info['summary_en_path'], 'r', encoding='utf-8') as f:
                        summary_en = f.read()
                    active_class = '' if file_info['has_summary_no'] else 'active'
                    summary_content += f'''
                    <div id="tab-en" class="tab-content {active_class}">
                        <pre>{summary_en}</pre>
                    </div>
                    '''
                except Exception as e:
                    self.logger.error(f"Error reading English summary: {e}")
        
        # Download links
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
        
        # Build header based on theme
        if self.current_theme == 'nostalgia':
            header_content = f"""
            <pre style="font-size: 6px;">{self._get_ascii_logo()}</pre>
            <div class="subtitle">🎵 {file_info['stem']}</div>
            """
        else:
            header_content = f"""
            <h1>🎵 {file_info['stem']}</h1>
            <p class="subtitle">Audio Player & Transcript</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 {file_info['stem']} - STENOGRAFEN</title>
    <style>{self._get_theme_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            {breadcrumb}
        </div>
        
        <div class="header">
            {header_content}
        </div>
        
        {audio_player}
        
        <div class="card">
            <h2>📝 Transcript</h2>
            <div class="transcript-section">
                {transcript_with_search}
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
        document.addEventListener('DOMContentLoaded', function() {{
            const searchInput = document.getElementById('searchInput');
            const searchResults = document.getElementById('searchResults');
            
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
                    const textSpan = line.querySelector('.text');
                    if (textSpan) {{
                        textSpan.innerHTML = textSpan.textContent;
                    }}
                }});
                searchResults.textContent = '';
                return;
            }}
            
            // Escape special regex characters
            const escapedQuery = query.replace(/[.*+?^${{}}()|[\\]]/g, '\\\\$&');
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
                    line.classList.remove('current');
                }});
                
                // Find and highlight current line
                const lines = document.querySelectorAll('.transcript-line');
                for (let i = 0; i < lines.length; i++) {{
                    const line = lines[i];
                    const lineTime = parseInt(line.getAttribute('data-time'));
                    const nextLineTime = i < lines.length - 1 ? 
                        parseInt(lines[i + 1].getAttribute('data-time')) : 
                        Infinity;
                    
                    if (currentTime >= lineTime && currentTime < nextLineTime) {{
                        line.classList.add('current');
                        // Auto-scroll to current line
                        line.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        break;
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
    parser.add_argument('--theme', choices=['nostalgia', 'modern'], help='Override theme from config (single theme)')
    parser.add_argument('--both', action='store_true', help='Generate BOTH themes with unified chooser page')
    
    args = parser.parse_args()
    
    try:
        generator = HTMLIndexGenerator(args.config)
        
        if args.both:
            # Generate both themes with unified hoofdindex
            print("🎨 Generating BOTH themes...")
            generator.generate_all_indexes(generate_both_themes=True)
            print("✅ HTML navigation system generated successfully with BOTH themes!")
            print("   - Nostalgia files: *-n.html")
            print("   - Modern files: *-m.html")
            print("   - Open hovedindex.html to choose your theme")
        else:
            # Override theme if specified
            if args.theme:
                generator.theme = args.theme
                generator.logger.info(f"Theme overridden to: {args.theme}")
            
            generator.generate_all_indexes(generate_both_themes=False)
            print(f"✅ HTML navigation system generated successfully with {generator.theme} theme!")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
