#!/usr/bin/env python3
"""
Export DOCX Summaries to TXT for HTML Display
Creates .txt versions of .docx summaries for web viewing
"""

import sys
from pathlib import Path
from typing import List
import argparse


def export_docx_to_txt(docx_path: Path) -> Path:
    """Export .docx file to .txt for HTML display"""
    try:
        from docx import Document
        
        # Read DOCX
        doc = Document(str(docx_path))
        
        # Extract text from all paragraphs
        text_content = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text)
        
        # Create .txt path
        txt_path = docx_path.with_suffix('.summary.txt')
        
        # Write to .txt
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        
        print(f"✅ Exported: {txt_path.name}")
        return txt_path
        
    except ImportError:
        print("❌ Error: python-docx not installed. Install with: pip install python-docx")
        return None
    except Exception as e:
        print(f"❌ Error exporting {docx_path.name}: {e}")
        return None


def find_docx_files(folder: Path, recursive: bool = True) -> List[Path]:
    """Find all .docx files in folder"""
    pattern = "**/*.docx" if recursive else "*.docx"
    return [f for f in folder.glob(pattern) if f.is_file() and not f.name.startswith('~')]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Export .docx summaries to .txt for HTML display"
    )
    parser.add_argument('folder', nargs='?', default='input', 
                       help='Folder to scan for .docx files')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Scan folders recursively')
    parser.add_argument('--file', help='Export specific file')
    
    args = parser.parse_args()
    
    if args.file:
        # Export single file
        docx_path = Path(args.file)
        if not docx_path.exists():
            print(f"❌ File not found: {docx_path}")
            sys.exit(1)
        
        if not docx_path.suffix == '.docx':
            print(f"❌ Not a .docx file: {docx_path}")
            sys.exit(1)
        
        result = export_docx_to_txt(docx_path)
        sys.exit(0 if result else 1)
    
    else:
        # Export all .docx files in folder
        folder = Path(args.folder)
        if not folder.exists():
            print(f"❌ Folder not found: {folder}")
            sys.exit(1)
        
        docx_files = find_docx_files(folder, args.recursive)
        
        if not docx_files:
            print(f"No .docx files found in {folder}")
            sys.exit(0)
        
        print(f"Found {len(docx_files)} .docx files")
        print()
        
        exported = 0
        for docx_file in docx_files:
            if export_docx_to_txt(docx_file):
                exported += 1
        
        print()
        print(f"✅ Exported {exported}/{len(docx_files)} files")


if __name__ == "__main__":
    main()
