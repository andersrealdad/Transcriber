# STENOGRAFEN Enhanced HTML Generator - Complete Package

## 📦 What's Included

This package contains everything you need to generate beautiful, professional HTML pages for your transcription system with **dual themes** and **dual-language summaries**.

### Files in This Package

1. **generate_index.py** (67KB) - Main HTML generator script
2. **config_updated.yaml** - Updated configuration with theme settings
3. **BOTH_THEMES_GUIDE.md** - Guide for generating both themes simultaneously
4. **QUICK_START.md** - Get started in 3 steps
5. **README_HTML_GENERATOR.md** - Detailed documentation
6. **THEME_COMPARISON.md** - Visual comparison of themes

## 🚀 Quick Start

```bash
# Copy files to your stenografen folder
cp generate_index.py /path/to/stenografen/
cp config_updated.yaml /path/to/stenografen/config.yaml

# Generate BOTH themes with chooser (RECOMMENDED)
python generate_index.py --both

# Open in browser
xdg-open input/hovedindex.html
```

## ✨ Key Features

### 1. Dual Theme System
- **Nostalgia Theme** (`-n.html`) - Black/green terminal aesthetic
- **Modern Theme** (`-m.html`) - Clean professional design
- **Theme Chooser** - Select theme on huvudindex page

### 2. Dual-Language Summaries
- Norwegian and English summaries in tabs
- One-click language switching
- Preserved markdown formatting

### 3. Interactive Transcripts
- **Clickable timestamps** - Jump to audio position
- **Auto-follow** - Highlights current line during playback
- **Search** - Find text across entire transcript
- **Auto-scroll** - Keeps current line visible

### 4. Smart Navigation
- Hierarchical folder structure
- Breadcrumb navigation
- Statistics dashboard
- Status badges per file

## 📖 Usage

### Generate Both Themes (Recommended)
```bash
python generate_index.py --both
```

Creates:
- Theme chooser on hlavedindex.html
- All pages in both themes (*-n.html and *-m.html)
- Perfect for flexibility!

### Generate Single Theme
```bash
# Nostalgia only
python generate_index.py --theme nostalgia

# Modern only
python generate_index.py --theme modern

# Use config.yaml setting
python generate_index.py
```

### Output Structure
```
input/
├── hovedindex.html           # Theme chooser (with --both)
├── folder1/
│   ├── folder_index-n.html   # Nostalgia folder index
│   ├── folder_index-m.html   # Modern folder index
│   ├── audio-n.html          # Nostalgia file page
│   ├── audio-m.html          # Modern file page
│   ├── audio.txt             # Transcript
│   ├── audio_no.md           # Norwegian summary
│   ├── audio_en.md           # English summary
│   └── audio.m4a             # Audio file
```

## 🎨 Theme Details

### Nostalgia Theme (-n.html)
- **Look:** Black background, green terminal text, ASCII art
- **Font:** Courier New monospace
- **Best For:** Internal use, tech demos, developer docs
- **Vibe:** Hacker/retro aesthetic

### Modern Theme (-m.html)
- **Look:** Blue gradients, white cards, clean typography
- **Font:** Segoe UI sans-serif
- **Best For:** Client presentations, court submissions, professional meetings
- **Vibe:** Clean, trustworthy, professional

## 📋 File Naming Convention

When using `--both`:
- Files ending in `-n.html` = Nostalgia theme
- Files ending in `-m.html` = Modern theme
- Navigation stays within selected theme

When using single theme:
- Files named `*.html` (no suffix)
- Standard navigation

## 🔧 Configuration

Edit `config.yaml`:

```yaml
html_generation:
  enabled: true
  auto_generate: true
  include_audio_player: true
  theme: "modern"  # Default theme (when not using --both)
```

## 📊 Feature Matrix

| Feature | Single Theme | Both Themes (--both) |
|---------|-------------|---------------------|
| Theme Chooser | ❌ | ✅ |
| File Suffix | None | -n / -m |
| Disk Space | 1x | 2x |
| Generation Time | 1x | 2x |
| Flexibility | Low | High |
| Files per Audio | 1 HTML | 2 HTML |

## 💡 Recommendations

### When to Use --both
✅ You want flexibility to switch themes
✅ Different audiences (tech team vs clients)
✅ Demoing the system
✅ Not sure which theme you prefer

### When to Use Single Theme
✅ Only one audience type
✅ Limited disk space
✅ Faster generation needed
✅ Simple deployment

## 🎯 Example Workflows

### Scenario 1: Internal + Client Use
```bash
# Generate both themes
python generate_index.py --both

# Share modern theme links with clients
# Share nostalgia theme links internally
```

### Scenario 2: Court Submission
```bash
# Generate modern theme only
python generate_index.py --theme modern

# Clean, professional look throughout
```

### Scenario 3: Developer Demo
```bash
# Generate nostalgia theme only
python generate_index.py --theme nostalgia

# Cool hacker aesthetic
```

## 🔍 What Gets Generated

For each audio file, the generator creates:

### Hlavedindex.html
- Statistics dashboard
- Folder overview
- Theme chooser (with --both)

### Folder Indexes
- List of files in folder
- Status badges
- Quick navigation

### File Pages
- Audio player with controls
- Clickable transcript with search
- Dual-language summary tabs (NO/EN)
- Download links
- Breadcrumb navigation

## 🚨 Requirements

- Python 3.6+
- PyYAML library: `pip install pyyaml --break-system-packages`
- Audio files with:
  - `.txt` transcripts with `[HH:MM:SS]` timestamps
  - `_no.md` Norwegian summaries (optional)
  - `_en.md` English summaries (optional)

## 📱 Browser Support

Both themes work on:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

All features work offline!

## 🐛 Troubleshooting

### No HTML generated
**Check:** Audio files exist in input folder
```bash
ls input/*.m4a
```

### Summaries not showing
**Check:** Summary files exist
```bash
ls input/*_no.md input/*_en.md
```

### Timestamps not clickable
**Fix:** Ensure format is `[HH:MM:SS] text`

### Theme not applying
**Fix:** Use `--both` or `--theme` flag

### Links broken with --both
**Check:** Using correct file suffix (-n or -m)

## 📈 Performance

**Single Theme:**
- ~100-200 files/second
- ~30KB per HTML page
- Very fast generation

**Both Themes:**
- ~50-100 files/second (2x slower)
- ~60KB per file (2x disk space)
- Still very fast!

Example: 100 audio files
- Single: ~2-3 seconds, ~3MB
- Both: ~4-6 seconds, ~6MB

## 🎓 Advanced Tips

1. **Bookmark chooser:** Save hovedindex.html for easy theme switching
2. **Mix themes:** Send `-m.html` to clients, `-n.html` to team
3. **Safe regeneration:** Can run multiple times safely
4. **Remove theme:** Delete all `*-n.html` or `*-m.html` files
5. **Custom CSS:** Edit theme methods in generate_index.py

## 📚 Documentation

- **BOTH_THEMES_GUIDE.md** - Using the --both flag
- **QUICK_START.md** - Get started in 3 steps
- **README_HTML_GENERATOR.md** - Detailed features
- **THEME_COMPARISON.md** - Visual theme comparison

## 🎉 You're Ready!

```bash
# Install
cp generate_index.py /path/to/stenografen/

# Generate
python generate_index.py --both

# Enjoy!
xdg-open input/hovedindex.html
```

---

**Created for the STENOGRAFEN legal transcription system**

Features:
✅ Dual themes (Nostalgia + Modern)
✅ Dual languages (Norwegian + English)
✅ Clickable timestamps
✅ Full-text search
✅ Auto-following playback
✅ Professional or hacker aesthetic
✅ Mobile responsive
✅ Works offline

Perfect for lawyers, developers, and anyone who needs beautiful transcript presentations! 🚀
