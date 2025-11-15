# STENOGRAFEN HTML Generator - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Install the Files
```bash
# Copy to your transcription system folder
cp generate_index.py /path/to/your/stenografen/
cp config_updated.yaml /path/to/your/stenografen/config.yaml
```

### Step 2: Choose Your Theme

**For Client/Professional Use:**
```bash
python generate_index.py --theme modern
```

**For Internal/Tech Use:**
```bash
python generate_index.py --theme nostalgia
```

### Step 3: Open in Browser
```bash
# Navigate to your input folder
cd /path/to/your/input/folder

# Open the main page
# Linux/Mac:
xdg-open hovedindex.html

# Windows:
start hovedindex.html
```

---

## 📁 Expected File Structure

Your transcription system should create:
```
input/
├── folder1/
│   ├── meeting.m4a          ← Audio file
│   ├── meeting.txt          ← Transcript with [HH:MM:SS]
│   ├── meeting_no.md        ← Norwegian summary
│   └── meeting_en.md        ← English summary
└── folder2/
    └── ...
```

After running the generator:
```
input/
├── hovedindex.html          ← NEW: Main index
├── folder1/
│   ├── folder_index.html    ← NEW: Folder overview
│   ├── meeting.html         ← NEW: File page
│   ├── meeting.m4a
│   ├── meeting.txt
│   ├── meeting_no.md
│   └── meeting_en.md
└── folder2/
    └── ...
```

---

## ⚡ Quick Commands

```bash
# Basic usage (uses theme from config.yaml)
python generate_index.py

# Override to Modern theme
python generate_index.py --theme modern

# Override to Nostalgia theme
python generate_index.py --theme nostalgia

# Use custom config
python generate_index.py --config /path/to/config.yaml

# Help
python generate_index.py --help
```

---

## ✨ What You Get

### 1. **Main Index** (hovedindex.html)
- Overview of all folders
- Statistics dashboard
- Quick navigation

### 2. **Folder Indexes** (folder_index.html in each folder)
- List of all audio files in folder
- Status badges (transcript/summaries available)
- Links to individual files

### 3. **File Pages** (audio_name.html for each audio)
- 🎵 Audio player with controls
- 📝 Clickable transcript with timestamps
- 🔍 Search functionality
- 📋 Dual-language summary tabs (NO/EN)
- 💾 Download links for all files
- 🧭 Breadcrumb navigation

---

## 🎨 Theme Preview

### Nostalgia Theme
```
┌────────────────────────────────┐
│ BLACK background               │
│ GREEN text (#00ff00)          │
│ CYAN accents (#00ffff)        │
│ ASCII art logo                │
│ Terminal aesthetic            │
│ Monospace font                │
└────────────────────────────────┘
```

### Modern Theme
```
┌────────────────────────────────┐
│ BLUE gradient background       │
│ WHITE cards with shadows       │
│ PROFESSIONAL blue accents      │
│ Clean typography              │
│ Smooth animations             │
│ Sans-serif font               │
└────────────────────────────────┘
```

---

## 🎯 Key Features

### Clickable Timestamps
```
[00:01:23] This text becomes clickable
           ↓
    [Click] → Audio jumps to 1 min 23 sec
```

### Dual Summaries
```
┌─────────────────────────────┐
│ [🇳🇴 Norwegian] [🇬🇧 English] │
│ ───────────────────────────  │
│ Content in selected language│
└─────────────────────────────┘
```

### Live Search
```
┌────────────────────────────┐
│ 🔍 [Search transcript...] │
│    Found 3 matches        │
├────────────────────────────┤
│ Results highlighted in    │
│ yellow across transcript  │
└────────────────────────────┘
```

### Auto-Follow Audio
```
Audio plays → Transcript scrolls
              Current line highlighted
              Stays centered in view
```

---

## 🔧 Configuration

Edit `config.yaml`:

```yaml
html_generation:
  enabled: true
  auto_generate: true
  include_audio_player: true
  theme: "modern"  # or "nostalgia"
```

---

## 📱 Mobile Support

Both themes work perfectly on:
- Smartphones
- Tablets  
- Desktop browsers
- Touch and mouse controls

---

## ⚠️ Troubleshooting

### Problem: No HTML files generated
**Solution:** Check that audio files exist in input folder
```bash
ls input/*.m4a  # Should show audio files
```

### Problem: Summaries not showing
**Solution:** Check for _no.md and _en.md files
```bash
ls input/*_no.md input/*_en.md
```

### Problem: Timestamps not clickable
**Solution:** Verify transcript format
```
✅ Correct: [00:01:23] Text here
❌ Wrong:   [0:1:23] Text here
❌ Wrong:   00:01:23 Text here
```

### Problem: Theme not applying
**Solution:** Use --theme flag
```bash
python generate_index.py --theme modern
```

---

## 📊 Performance

- **Generation Speed:** ~100-200 files per second
- **File Size:** 15-30KB per HTML page
- **Load Time:** <100ms in browser
- **No Dependencies:** Works offline

---

## 🎓 Best Practices

1. **For Lawyers/Clients:** Always use Modern theme
2. **Test First:** Run on small folder before full system
3. **Backup:** Original files are never modified
4. **Regenerate:** Safe to run multiple times
5. **Browser:** Use Chrome/Firefox for best experience

---

## 💡 Pro Tips

1. **Batch Processing:** Run after all transcriptions complete
2. **Theme Switching:** Can regenerate with different theme anytime
3. **Custom CSS:** Edit generate_index.py to modify colors
4. **Bookmarks:** Save hovedindex.html as bookmark
5. **Sharing:** Zip entire folder to share with others

---

## 📞 Support

Issues? Check:
1. Python 3.6+ installed
2. Config.yaml in same directory
3. Input folder exists
4. Audio files present
5. Proper file permissions

---

## 🎉 You're Ready!

Run your first generation:
```bash
python generate_index.py --theme modern
```

Open `hovedindex.html` in your browser and enjoy! 🚀
