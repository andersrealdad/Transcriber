#!/usr/bin/env python3
"""
Link validation and cleanup script for STENOGRAFEN HTML files
"""

import os
import yaml
from pathlib import Path
import logging
from typing import Dict, List, Set

class LinkValidator:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.input_folder = Path(self.config['folders']['input'])
        
    def scan_existing_files(self) -> Dict[str, Set[str]]:
        """Scan for existing transcription and summary files"""
        files = {
            'transcripts': set(),
            'summaries_no': set(),
            'summaries_en': set(),
            'audio': set(),
            'html': set()
        }
        
        # Scan for files
        for txt_file in self.input_folder.rglob("*.txt"):
            files['transcripts'].add(str(txt_file.relative_to(self.input_folder)))
        
        for md_file in self.input_folder.rglob("*_no.md"):
            files['summaries_no'].add(str(md_file.relative_to(self.input_folder)))
            
        for md_file in self.input_folder.rglob("*_en.md"):
            files['summaries_en'].add(str(md_file.relative_to(self.input_folder)))
            
        for html_file in self.input_folder.rglob("*.html"):
            if html_file.name not in ["hovedindex.html", "folder_index.html"]:
                files['html'].add(str(html_file.relative_to(self.input_folder)))
        
        # Scan for audio files
        audio_extensions = [f".{ext}" for ext in self.config['audio']['formats']]
        for audio_file in self.input_folder.rglob("*"):
            if audio_file.suffix.lower() in audio_extensions:
                files['audio'].add(str(audio_file.relative_to(self.input_folder)))
        
        return files
    
    def regenerate_html_structure(self):
        """Regenerate HTML structure with current files"""
        self.logger.info("Regenerating HTML structure...")
        
        try:
            from generate_index import HTMLIndexGenerator
            generator = HTMLIndexGenerator()
            generator.generate_all_indexes()
            self.logger.info("HTML structure regenerated successfully")
        except Exception as e:
            self.logger.error(f"HTML generation failed: {e}")
    
    def validate_and_cleanup(self):
        """Main validation and cleanup process"""
        self.logger.info("Starting link validation and cleanup...")
        
        # Scan existing files
        files = self.scan_existing_files()
        
        self.logger.info(f"Found {len(files['transcripts'])} transcripts")
        self.logger.info(f"Found {len(files['summaries_no'])} Norwegian summaries")
        self.logger.info(f"Found {len(files['summaries_en'])} English summaries")
        self.logger.info(f"Found {len(files['html'])} HTML files")
        self.logger.info(f"Found {len(files['audio'])} audio files")
        
        # Check for orphaned files
        self._check_orphaned_files(files)
        
        # Clean up old HTML files if needed
        self._cleanup_old_html_files()
        
        # Regenerate HTML structure
        self.regenerate_html_structure()
        
        self.logger.info("Validation and cleanup complete!")
    
    def _check_orphaned_files(self, files: Dict[str, Set[str]]):
        """Check for orphaned summary files without corresponding transcripts"""
        transcript_stems = {Path(t).stem for t in files['transcripts']}
        
        # Check Norwegian summaries
        for summary_no in files['summaries_no']:
            stem = Path(summary_no).stem.replace('_no', '')
            if stem not in transcript_stems:
                self.logger.warning(f"Orphaned Norwegian summary: {summary_no}")
        
        # Check English summaries
        for summary_en in files['summaries_en']:
            stem = Path(summary_en).stem.replace('_en', '')
            if stem not in transcript_stems:
                self.logger.warning(f"Orphaned English summary: {summary_en}")
    
    def _cleanup_old_html_files(self):
        """Remove old HTML files that might be outdated"""
        try:
            # Find and remove old hovedindex.html files in subfolders
            for html_file in self.input_folder.rglob("hovedindex.html"):
                if html_file.parent != self.input_folder:
                    self.logger.info(f"Removing old hovedindex.html: {html_file}")
                    html_file.unlink()
            
            # Find and remove old folder_index.html files that might be stale
            for html_file in self.input_folder.rglob("folder_index.html"):
                # Check if folder still contains audio files
                folder = html_file.parent
                audio_extensions = [f".{ext}" for ext in self.config['audio']['formats']]
                has_audio = any(f.suffix.lower() in audio_extensions for f in folder.iterdir() if f.is_file())
                
                if not has_audio:
                    self.logger.info(f"Removing folder_index.html from empty folder: {html_file}")
                    html_file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    validator = LinkValidator()
    validator.validate_and_cleanup()

if __name__ == "__main__":
    main()
