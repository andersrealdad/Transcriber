# Quick Reference Card

One-page cheat sheet for common tasks.

---

## 🚀 Installation
```bash
chmod +x install.sh && ./install.sh
```

---

## 📝 Basic Usage

### Single Folder
```bash
cp audio.mp3 input/
./run_transcribe.sh
```

### Nested Folders (Fire & Forget!)
```bash
# Your structure
input/
├── meeting1/audio.mp3
├── meeting2/audio.mp3
└── meeting3/audio.mp3

# Run once
./run_transcribe.sh

# All folders processed automatically!
```

---

## 🎯 Common Commands

| Task | Command |
|------|---------|
| **Standard transcription** | `./run_transcribe.sh` |
| **Multi-pass (best quality)** | `./run_transcribe.sh config_multipass.yaml` |
| **Check system** | `./check_system.sh` |
| **Change AI model** | `./select_ollama_model.sh` |
| **Monitor progress** | `./monitor_progress.sh input` |
| **Resume interrupted** | `./run_transcribe.sh` (auto-skips done files) |

---

## ⚙️ Quick Config Changes

### Faster Processing
```yaml
whisper.model_size: "medium"
audio.ai_denoise.enabled: false
ollama.enabled: false
```

### Better Quality
```yaml
whisper.beam_size: 10
audio.ai_denoise.method: "both"
multi_pass.enabled: true
```

### Multi-Pass Only on Noisy Files
1. Process all: `./run_transcribe.sh`
2. Move bad ones: `mv bad_audio.mp3 input/difficult/`
3. Re-run: `./run_transcribe.sh config_multipass.yaml`

---

## 📊 Output Files

| File | Content |
|------|---------|
| `file.txt` | Transcription with timestamps |
| `file.md` | AI summary with key topics |
| `file_none.txt` | Multi-pass: no denoising |
| `file_demucs.txt` | Multi-pass: Demucs only |
| `file_deepfilternet.txt` | Multi-pass: DeepFilterNet only |
| `file_both.txt` | Multi-pass: both denoisers |
| `file.srt` | Subtitles (if enabled) |
| `file.json` | Full metadata |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **GPU not working** | `nvidia-smi` then reinstall PyTorch |
| **Out of memory** | Use smaller model: `medium` or `small` |
| **Too slow** | Disable multi-pass or AI denoising |
| **Ollama error** | `sudo systemctl restart ollama` |
| **Wrong language** | Set `language: "no"` or `"en"` |
| **Process interrupted** | Just re-run, it skips completed files |

---

## ⏱️ Time Estimates (1hr audio on RTX 3080)

| Mode | Time | Quality |
|------|------|---------|
| Fast | 3 min | Good |
| Standard | 5 min | Excellent |
| Multi-pass | 25 min | Best |

**20 meetings:**
- Standard: ~2 hours
- Multi-pass: ~8 hours (perfect for overnight!)

---

## 📁 Folder Structures

### Input: Nested Folders ✅
```
input/
├── meeting1/audio.mp3, notes.pdf
├── meeting2/audio.mp3, notes.pdf
└── projects/
    ├── project1/audio.mp3
    └── project2/audio.mp3
```

### Output: Structure Preserved
```
output/
├── meeting1/audio.txt, audio.md, notes.txt
├── meeting2/audio.txt, audio.md, notes.txt
└── projects/
    ├── project1/audio.txt, audio.md
    └── project2/audio.txt, audio.md
```

---

## 🎛️ Config Quick Edits

### Edit Config
```bash
nano config.yaml
# or
code config.yaml
```

### Key Settings
```yaml
# Folders
folders:
  input: "./input"
  output: ""  # Empty = same folder as input

# Quality vs Speed
whisper.model_size: "large-v3"  # or "medium", "small"
whisper.beam_size: 5  # Higher = better, slower (1-10)

# Denoising
audio.ai_denoise.method: "demucs"  # or "deepfilternet", "both", "none"

# Multi-pass
multi_pass.enabled: false  # Set true for difficult audio

# Summaries
ollama.enabled: true
ollama.model: "llama3.2"  # or mistral, llama3.1, etc.
```

---

## 🎯 Workflows

### 1. Quick Daily Use
```bash
cp audio.mp3 input/ && ./run_transcribe.sh
```

### 2. Batch Overnight
```bash
# Add all files
cp -r meetings/* input/

# Start with progress monitor
./run_transcribe.sh config_multipass.yaml &
./monitor_progress.sh input

# Detach and sleep
# Ctrl+Z, bg, disown
```

### 3. Test New Settings
```bash
# Small test batch
mkdir input_test
cp test_audio.mp3 input_test/

# Edit config, test
./run_transcribe.sh

# If good, run full batch
```

---

## 💡 Pro Tips

### Resume Interrupted Jobs
```yaml
processing.skip_existing: true  # Already default!
```
Just re-run the same command!

### Save Disk Space
```yaml
multi_pass.keep_individual: false  # Only keep merged
```

### Only Transcribe (Skip Summaries)
```yaml
ollama.enabled: false
```

### Check What's Done
```bash
find input -name "*.txt" -mmin -60  # Last hour
find input -name "*.txt" | wc -l    # Total count
```

### Run in Background
```bash
nohup ./run_transcribe.sh > log.txt 2>&1 &
tail -f log.txt  # Watch progress
```

---

## 🆘 Emergency Commands

### Kill Stuck Process
```bash
pkill -f transcribe.py
```

### Clear Cache and Restart
```bash
rm -rf __pycache__ .requirements_installed
./run_transcribe.sh
```

### Free Up Disk Space
```bash
# Remove multi-pass individual files
find input -name "*_none.txt" -delete
find input -name "*_demucs.txt" -delete
find input -name "*_deepfilternet.txt" -delete
find input -name "*_both.txt" -delete
```

### Check GPU Usage
```bash
watch -n 1 nvidia-smi
```

---

## 📚 Full Documentation

- **Quick Start**: `QUICK_START.md`
- **Batch Processing**: `BATCH_PROCESSING.md`
- **Full Manual**: `README.md`
- **Config Examples**: `config_examples.md`
- **Project Overview**: `PROJECT_SUMMARY.md`

---

## 🔑 Most Used Commands

```bash
# 1. Standard processing
./run_transcribe.sh

# 2. Maximum quality  
./run_transcribe.sh config_multipass.yaml

# 3. Check progress
./monitor_progress.sh input

# 4. Change AI model
./select_ollama_model.sh

# 5. Resume after interruption
./run_transcribe.sh  # Just run again!
```

---

**Happy transcribing! 🎙️→📝**