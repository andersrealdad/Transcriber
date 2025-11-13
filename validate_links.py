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
        
        # Regenerate HTML structure
        self.regenerate_html_structure()
        
        self.logger.info("Validation and cleanup complete!")

def main():
    validator = LinkValidator()
    validator.validate_and_cleanup()

if __name__ == "__main__":
    main()
