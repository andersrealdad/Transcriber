cat << EOF > flow.md
🔀 Recommended Workflow:
1. Start fresh chat with the architect (me or another Claude)
   * Upload: `transcribe.py` + `config.yaml` + `final_summary.md`
   * Say: "Review this transcription system. I want to add: [watchdog/dual-language/webhooks]. What should I consider before implementing?"
2. Get architectural feedback BEFORE coding:
   * Potential conflicts/issues
   * Better design patterns
   * Edge cases you haven't thought of
   * Integration points
3. Then use Aider recipes once you have the plan
💡 Why This Works:
* Fresh context = better architectural overview
* No token waste from our long debugging history
* Clean slate for design discussions
* You can reference this chat for the Aider recipes
📋 Template for New Chat:
========================================
Processing completed successfully!
========================================
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ aider --version
aider 0.86.1
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ export ANTHROPIC_API_KEY=
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ echo ANTHROPIC_API_KEY=
ANTHROPIC_API_KEY=
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ export ANTHROPIC_API_KEY="your-api-key-here"
# Note: Use .env file instead of exporting keys in the shell
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ echo ANTHROPIC_API_KEY=
ANTHROPIC_API_KEY=
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ cat recipe_1md
cat: recipe_1md: No such file or directory
(venv) EMPIRE:/mnt/c/Empire/Transcriber $ cat recipe_1.md
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

\`\`\`
I have a working audio transcription system using Faster-Whisper + Demucs + Ollama. 
add:
/mnt/c/Empire/Transcriber/config.yaml
/mnt/c/Empire/Transcriber/transcribe.py
Current features: [list from final_summary.md]
### Core Features
- ✅ **GPU-accelerated transcription** using Faster-Whisper on RTX 3080
- ✅ **AI-powered audio denoising** (Demucs + DeepFilterNet)
- ✅ **Multi-stage enhancement pipeline** (AI → FFmpeg → Whisper VAD)
- ✅ **Multi-pass transcription** for difficult audio (NEW! 🔥)
- ✅ **LLM-powered merge** - AI picks best text from multiple passes
- ✅ **Ollama integration** for intelligent summaries
- ✅ **Nested folder support** - "fire and forget" batch processing
- ✅ **OCR for PDFs** with Norwegian + English support
- ✅ **Auto language detection** (Norwegian/English/90+ languages)
- ✅ **Multiple output formats** (TXT, SRT, VTT, JSON, Markdown)
- ✅ **Processing metadata** - tracks which enhancements were used

I want to add:
. Dual-language summaries (NO + EN)

Review the architecture and tell me:
- Best approach for each feature
- Potential conflicts/issues
- Implementation order
- Any config changes needed

Then I'll use Aider to implement with your guidance.
\`\`\`
EOF
