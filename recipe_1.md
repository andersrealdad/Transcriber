Based on your recommendations, I want to start with dual-language summaries first, then add self-contained HTML output.

Here's my implementation plan:

1. Add dual-language summary support to transcribe.py:
   - In generate_summary() method (line ~620), after generating the first summary:
     * Check if summary.dual_language is enabled in config
     * If original language != target language, generate second summary
     * Save as file.md (original lang) and file_en.md (English) or file_no.md (Norwegian)
   	
2. Add self-contained HTML index generation:
   - Create generate_html_index() method that:
     * Generates HTML page with ASCII "STENOGRAFEN" header
     * Lists all transcripts and summaries with language toggle
     * Preserves nested folder structure from /input to /output
     * Creates parallel /media folder structure for improved audio clips
     * Links audio files in HTML using relative paths to /media
     * Footer with: GitHub link, your name, phone number
   - Each HTML serves as index.html in its folder
   - Keep it DRY: single template, populate with folder contents
   
3. Folder structure output:
   /output
     /project_name
       index.html          # STENOGRAFEN index
       transcript_no.md
       transcript_en.md
       summary_no.md
       summary_en.md
   /media
     /project_name
       original.wav        # or .mp3
       demucs_vocals.wav

4. Add to config.yaml:
   ollama.summary:
     dual_language:
       enabled: true
       languages: ["no", "en"]
   
   output:
     generate_html: true
     html_template: "stenografen"  # ASCII header style
     preserve_folder_structure: true
     media_folder: "../media"      # relative path from output
   
   contact:
     name: "[Anders Iversen]"
     phone: "[+47 97 41 75 26]"
     github: "[@andersrealdad]"

Does this align with your architectural suggestions? Any issues I should address first?
