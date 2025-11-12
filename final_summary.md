# 🎙️ AI-Powered Transcription & OCR System

Complete audio transcription and PDF OCR system with AI denoising and Ollama-powered summaries.

## 📦 What You Get

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

### Files Included

```
📁 Project Files
├── config.yaml                  # Main configuration
├── transcribe.py                # Python transcription engine
├── run_transcribe.sh           # Main launcher script
├── check_system.sh             # System requirements checker
├── select_ollama_model.sh      # Easy model switcher
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
├── QUICK_START.md              # Quick setup guide
└── PROJECT_SUMMARY.md          # This file
```

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
# System packages
sudo apt-get update && sudo apt-get install -y \
    ffmpeg tesseract-ocr tesseract-ocr-eng tesseract-ocr-nor poppler-utils python3-dev python3-venv

# Make scripts executable
chmod +x *.sh
```

### 2. First Run
```bash
# This will auto-install everything
./run_transcribe.sh
```

### 3. Process Files
```bash
# Add files to input folder
cp your_audio.mp3 input/
cp your_document.pdf input/

# Process
./run_transcribe.sh

# Check outputs
ls input/
# your_audio.txt  (transcription with timestamps)
# your_audio.md   (AI summary)
# your_document.txt (OCR result)
```

---

## ⚙️ How It Works

### Audio Processing Pipeline

```
📥 Input Audio (MP3/WAV/M4A/FLAC/etc.)
    ↓
🔊 Stage 1: AI Denoising
    ├─ Demucs: Isolate vocals from background
    └─ DeepFilterNet: Remove stationary noise
    ↓
🎚️ Stage 2: FFmpeg Enhancement
    ├─ High-pass filter (remove rumble)
    ├─ Adaptive noise reduction
    └─ Audio normalization
    ↓
🤖 Stage 3: Whisper Transcription (GPU)
    ├─ Auto language detection
    ├─ VAD (Voice Activity Detection)
    └─ Generate timestamped segments
    ↓
🧠 Stage 4: Ollama Summary (Optional)
    ├─ Analyze full transcription
    ├─ Extract key topics
    └─ Generate markdown summary
    ↓
📤 Output
    ├─ .txt (transcription + timestamps)
    ├─ .md (AI summary)
    ├─ .srt (subtitles)
    └─ .json (full metadata)
```

### PDF OCR Pipeline

```
📄 Input PDF
    ↓
🖼️ Convert to Images (300 DPI)
    ↓
🔍 Tesseract OCR (English + Norwegian)
    ↓
📝 Extract Text by Page
    ↓
📤 Output .txt file
```

---

## 🎛️ Configuration Options

### Audio Quality Presets

**Maximum Quality** (Best for important content)
```yaml
whisper:
  model_size: "large-v3"
  beam_size: 10

audio:
  ai_denoise:
    method: "both"  # Demucs + DeepFilterNet
  enhance: true
```

**Balanced** (Default - Recommended)
```yaml
whisper:
  model_size: "large-v3"
  beam_size: 5

audio:
  ai_denoise:
    method: "demucs"
  enhance: true
```

**Fast** (Quick processing)
```yaml
whisper:
  model_size: "medium"
  beam_size: 3

audio:
  ai_denoise:
    enabled: false
  enhance: true
```

### Ollama Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| llama3.2 | ⚡⚡⚡ | ⭐⭐⭐⭐ | General use (recommended) |
| llama3.1 | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex summaries |
| mistral | ⚡⚡⚡ | ⭐⭐⭐⭐ | Multilingual (NO/EN) |
| gemma2 | ⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| qwen2.5 | ⚡⚡ | ⭐⭐⭐⭐ | Strong Norwegian |

Change model easily:
```bash
./select_ollama_model.sh
```

---

## 📊 Performance

### Your RTX 3080 (10GB VRAM)

| Task | Speed | Notes |
|------|-------|-------|
| Transcription (large-v3) | 20-30x realtime | 1hr audio → ~3 min |
| AI Denoising (Demucs) | ~1x realtime | 1hr audio → ~1 min |
| AI Denoising (DeepFilterNet) | ~2x realtime | 1hr audio → ~30 sec |
| Ollama Summary | Variable | 30 sec - 2 min |

**Total Time (1hr audio):** ~5-8 minutes with all features enabled

### GPU Memory Usage

| Process | VRAM Usage |
|---------|------------|
| Whisper large-v3 | ~8GB |
| Ollama llama3.2 | ~2GB |
| Both (sequential) | No conflict ✅ |

Since transcription finishes before summary generation, no GPU memory conflicts!

---

## 🌍 Language Support

### Auto-Detection
- Set `language: null` in config
- Whisper detects 90+ languages automatically
- Works perfectly for Norwegian/English mix

### Supported Languages (Whisper)
Norwegian (Bokmål/Nynorsk), English, Swedish, Danish, German, French, Spanish, Italian, Dutch, Polish, Portuguese, Russian, Turkish, Arabic, Chinese, Japanese, Korean, and 70+ more

### OCR Languages (Tesseract)
- English (eng)
- Norwegian (nor)
- Can add more: `sudo apt-get install tesseract-ocr-[lang]`

---

## 🛠️ Utility Scripts

### check_system.sh
Verifies all dependencies are installed:
```bash
./check_system.sh
```

Checks:
- ✅ GPU and CUDA
- ✅ Python and packages
- ✅ FFmpeg and Tesseract
- ✅ Ollama and models
- ✅ System requirements

### select_ollama_model.sh
Easy model switching:
```bash
./select_ollama_model.sh
```

Features:
- Lists installed models
- Pull new models
- Update config automatically
- Test model connectivity

---

## 📁 Example Workflows

### Workflow 1: Norwegian Podcast → English Summary
```yaml
# config.yaml
whisper:
  language: null  # Auto-detect

ollama:
  summary:
    language: "en"  # Summary in English
```

Output:
- `podcast.txt` - Norwegian transcription
- `podcast.md` - English summary

### Workflow 2: Batch Lecture Processing
```bash
# Add all lectures
cp lectures/*.mp3 input/

# Process once
./run_transcribe.sh

# Get:
# - lecture1.txt + lecture1.md
# - lecture2.txt + lecture2.md
# - lecture3.txt + lecture3.md
```

### Workflow 3: Maximum Quality Interview
```yaml
audio:
  ai_denoise:
    method: "both"
  
whisper:
  model_size: "large-v3"
  beam_size: 10

ollama:
  model: "llama3.1"  # Better model
  summary:
    style: "detailed"
    max_length: 800
```

### Workflow 4: Fast Transcription Only
```yaml
ollama:
  enabled: false

audio:
  ai_denoise:
    enabled: false

whisper:
  model_size: "medium"
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Out of Memory**
```yaml
# Use smaller model
whisper:
  model_size: "medium"
```

**2. Slow Processing**
```yaml
# Disable AI denoising
audio:
  ai_denoise:
    enabled: false
```

**3. Ollama Not Responding**
```bash
# Restart Ollama
sudo systemctl restart ollama

# Or run in foreground
ollama serve
```

**4. Poor Transcription Quality**
```yaml
# Increase beam size
whisper:
  beam_size: 8  # or 10

# Enable both denoisers
audio:
  ai_denoise:
    method: "both"
```

**5. Wrong Language Detected**
```yaml
# Force specific language
whisper:
  language: "no"  # or "en"
```

---

## 💡 Pro Tips

1. **First Time?** Run `./check_system.sh` to verify setup
2. **Testing?** Start with a short audio file
3. **Batch Processing?** Put all files in `input/` and run once
4. **Resume Support?** Enable `skip_existing: true`
5. **Clean Audio?** Disable AI denoising for 2x speed
6. **Very Noisy?** Use `method: "both"` for best results
7. **Different Summary Style?** Try different Ollama models
8. **Mixed Languages?** Keep auto-detection enabled
9. **Long Files?** No problem - handles hours of audio
10. **Want Subtitles?** Set `format: "srt"` or `"all"`

---

## 📚 Additional Resources

### Documentation
- **QUICK_START.md** - Step-by-step setup
- **README.md** - Detailed documentation
- **config.yaml** - All settings explained

### External Links
- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- Ollama Models: https://ollama.ai/library
- Tesseract Languages: https://github.com/tesseract-ocr/tessdata

---

## 🎯 What Makes This Special

### vs. Cloud Services (Whisper API, Rev, etc.)
- ✅ **Free unlimited usage**
- ✅ **Complete privacy** (all local)
- ✅ **Better quality** (latest models, customizable)
- ✅ **No file size limits**
- ✅ **Offline capable**

### vs. Basic Whisper Scripts
- ✅ **AI-powered denoising** (not just FFmpeg)
- ✅ **Intelligent summaries** (Ollama integration)
- ✅ **Complete pipeline** (audio + PDF)
- ✅ **Production-ready** (error handling, logging)
- ✅ **Easy configuration** (no code changes needed)

### vs. Manual Transcription
- ✅ **20-30x faster**
- ✅ **Consistent quality**
- ✅ **Timestamps included**
- ✅ **Searchable text**
- ✅ **AI summaries**

---

## 🚦 Status Indicators

When running, you'll see:
- 🟢 **Green**: Success
- 🟡 **Yellow**: Warning (non-critical)
- 🔵 **Blue**: Information
- 🔴 **Red**: Error

Progress bars show:
- Current file being processed
- Percentage complete
- Estimated time remaining

---

## ⚡ Next Steps

1. ✅ Run `./check_system.sh` to verify setup
2. ✅ Review `config.yaml` settings
3. ✅ Add test file to `input/`
4. ✅ Run `./run_transcribe.sh`
5. ✅ Review output quality
6. ✅ Adjust config if needed
7. ✅ Process your files!

---

## 📞 Need Help?

1. Check `./check_system.sh` output
2. Review config.yaml comments
3. Read QUICK_START.md
4. Check logs in console output

---

**Happy Transcribing! 🎙️→📝✨**

*Powered by Faster-Whisper, Ollama, Demucs, DeepFilterNet, and your RTX 3080*