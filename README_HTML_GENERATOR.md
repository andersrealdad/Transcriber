# STENOGRAFEN - Enhanced HTML Generator

## Features

### 🎨 Dual Theme Support
- **Nostalgia Theme**: Black/green terminal aesthetic with ASCII art logo - perfect for the hacker vibe
- **Modern Theme**: Clean, professional design with gradients and smooth animations - perfect for client presentations

### 📋 Dual-Language Summaries
- Automatically displays both Norwegian and English summaries in tabs
- Easy switching between languages with one click
- Preserves markdown formatting

### ⏱️ Clickable Timestamps
- Every timestamp `[HH:MM:SS]` in transcripts is clickable
- Clicking jumps directly to that position in the audio
- Current playing line is highlighted automatically
- Auto-scrolls to follow audio playback

### 🔍 Full-Text Search
- Search across entire transcript
- Real-time highlighting of matches
- Shows match count

### 📁 Smart Navigation
- Hierarchical folder structure
- Breadcrumb navigation
- Statistics dashboard on main page
- Status badges for each file (transcript/summaries available)

## Installation

1. Make sure you have the required dependencies:
```bash
pip install pyyaml --break-system-packages
```

2. Copy the files to your transcription system folder:
   - `generate_index.py` (main generator)
   - `config.yaml` (updated with theme settings)

## Usage

### Basic Usage
Generate HTML with the theme specified in config.yaml:
```bash
python generate_index.py
```

### Override Theme
Generate with **Nostalgia** theme (black/green hacker):
```bash
python generate_index.py --theme nostalgia
```

Generate with **Modern** theme (clean professional):
```bash
python generate_index.py --theme modern
```

### Using Custom Config
```bash
python generate_index.py --config /path/to/config.yaml
```

## Configuration

Edit `config.yaml` to set your preferred theme:

```yaml
html_generation:
  enabled: true
  auto_generate: true
  include_audio_player: true
  theme: "modern"  # Options: "nostalgia" or "modern"
```

### Theme Comparison

**Nostalgia Theme** - For internal use / tech demos:
- Black background (#0a0a0a)
- Green terminal text (#00ff00)
- ASCII art STENOGRAFEN logo
- Terminal/hacker aesthetic
- Cyan accents (#00ffff)
- Monospace font (Courier New)

**Modern Theme** - For client presentations:
- Clean gradient background
- Professional white cards
- Sans-serif fonts (Segoe UI)
- Smooth animations
- Blue accents (#3498db)
- Fully responsive design

## Output Structure

The generator creates:

```
input/
├── hovedindex.html              # Main index with statistics
├── folder1/
│   ├── folder_index.html        # Folder overview
│   ├── audio1.html              # Individual file page
│   ├── audio1.txt               # Transcript
│   ├── audio1_no.md             # Norwegian summary
│   ├── audio1_en.md             # English summary
│   └── audio1.m4a               # Audio file
└── folder2/
    └── ...
```

## File Page Features

Each audio file page includes:

1. **Audio Player**
   - Full HTML5 audio controls
   - Preload metadata for faster loading
   - Shows filename

2. **Transcript Section**
   - Search functionality
   - Clickable timestamps
   - Auto-scroll following playback
   - Current line highlighting

3. **Summary Tabs**
   - Norwegian (🇳🇴)
   - English (🇬🇧)
   - Preserved markdown formatting

4. **Download Links**
   - Transcript (.txt)
   - Norwegian summary (.md)
   - English summary (.md)

5. **Navigation**
   - Breadcrumb trail
   - Back to folder
   - Home link

## Requirements

Your transcription system should generate these files:
- `audio.txt` - Transcript with [HH:MM:SS] timestamps
- `audio_no.md` - Norwegian summary (optional)
- `audio_en.md` - English summary (optional)
- `audio.m4a` (or other audio format)

## Timestamp Format

The generator supports these timestamp formats:
- `[HH:MM:SS]` - Hours, minutes, seconds (e.g., [01:23:45])
- `[MM:SS]` - Minutes, seconds (e.g., [12:34])

Example transcript line:
```
[00:02:17] Jeg vet ikke hvor lang tid det tar å kopiere over det.
```

## Browser Compatibility

Tested on:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## Tips

1. **For lawyers/clients**: Use `--theme modern` for professional, clean look
2. **For internal use**: Use `--theme nostalgia` for the cool terminal vibe
3. **Regenerate anytime**: Safe to run multiple times, won't delete audio/transcripts
4. **Search works offline**: No internet required for any features

## Troubleshooting

### No summaries showing
- Check that `audio_no.md` and `audio_en.md` exist in the same folder as the audio
- Check file permissions

### Timestamps not clickable
- Ensure transcript uses correct format: `[HH:MM:SS]` or `[MM:SS]`
- Space required after timestamp: `[00:01:23] text here`

### Theme not applying
- Check `config.yaml` has `html_generation.theme` set
- Try using `--theme` flag to override
- Check for typos (must be exactly "nostalgia" or "modern")

## Support

For issues or questions:
- Check log output: script shows detailed progress
- Verify config.yaml is in the same directory
- Ensure input folder exists and contains audio files

## License

Part of the STENOGRAFEN transcription system.
Created for legal transcription workflows.
