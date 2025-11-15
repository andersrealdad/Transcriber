# STENOGRAFEN - Generate Both Themes

## 🎨 New Feature: Generate BOTH Themes Simultaneously!

You can now generate **both** Nostalgia and Modern themes at the same time, and choose which one to view from a unified hovedindex page!

## Quick Usage

```bash
# Generate BOTH themes with theme chooser
python generate_index.py --both
```

This creates:
- `hovedindex.html` - Theme chooser page (choose Nostalgia or Modern)
- `*-n.html` files - Nostalgia theme pages
- `*-m.html` files - Modern theme pages

## File Structure

```
input/
├── hovedindex.html              # Theme chooser (select Nostalgia or Modern)
├── folder1/
│   ├── folder_index-n.html      # Nostalgia folder index
│   ├── folder_index-m.html      # Modern folder index
│   ├── audio1-n.html            # Nostalgia file page
│   ├── audio1-m.html            # Modern file page
│   ├── audio1.txt
│   ├── audio1_no.md
│   ├── audio1_en.md
│   └── audio1.m4a
```

## All Commands

```bash
# Generate BOTH themes (recommended)
python generate_index.py --both

# Generate single theme (Nostalgia only)
python generate_index.py --theme nostalgia

# Generate single theme (Modern only)
python generate_index.py --theme modern

# Use theme from config.yaml
python generate_index.py
```

## Theme Chooser Page

When you use `--both`, the `hovedindex.html` shows a theme chooser:

```
┌────────────────────────────────────┐
│        STENOGRAFEN                 │
│  Legal Transcription System        │
│                                    │
│  Choose your viewing experience    │
│                                    │
│  [🖥️ NOSTALGIA]  [🎯 MODERN]      │
│   Terminal Style   Professional    │
└────────────────────────────────────┘
```

Click your preferred theme to browse with that style!

## Benefits of --both

✅ **Flexibility** - Switch between themes anytime
✅ **Client-Ready** - Show Modern to clients, use Nostalgia internally
✅ **Demo-Friendly** - Perfect for showing both options
✅ **No Re-generation** - Both available instantly

## File Naming Convention

- `-n.html` suffix = **Nostalgia** theme (green/black terminal)
- `-m.html` suffix = **Modern** theme (clean professional)

## When to Use What

### Use `--both` when:
- You want flexibility to switch themes
- Showing to different audiences (tech vs clients)
- Demoing the system
- Not sure which theme you prefer

### Use `--theme nostalgia` when:
- Only need terminal aesthetic
- Internal use only
- Saving disk space (half the files)

### Use `--theme modern` when:
- Only need professional look
- Client presentations only
- Court submissions
- Saving disk space (half the files)

## Disk Space

**Single Theme:** ~30KB per file × number of files
**Both Themes:** ~60KB per file × number of files

Example: 100 audio files
- Single theme: ~3MB total
- Both themes: ~6MB total

**Recommendation:** Use `--both` unless disk space is critical!

## Performance

Generation time with `--both`:
- Processes each file twice (once per theme)
- Takes approximately **2x** as long
- Still very fast: ~200 files in 10-15 seconds

## Example Workflow

```bash
# 1. Transcribe your audio files
python stenografen.py

# 2. Generate both themes
python generate_index.py --both

# 3. Open in browser
xdg-open input/hovedindex.html  # Linux
open input/hovedindex.html      # Mac
start input\hovedindex.html     # Windows

# 4. Choose your theme and browse!
```

## Theme Comparison

| Feature | Nostalgia (-n) | Modern (-m) |
|---------|---------------|-------------|
| Background | Black | Blue Gradient |
| Text | Green Terminal | Professional |
| Logo | ASCII Art | Clean Text |
| Best For | Internal/Tech | Clients/Court |
| Links End | `-n.html` | `-m.html` |

## Switching Themes

With `--both`, you can:
1. Open `hovedindex.html`
2. Click theme chooser anytime
3. Navigate freely within that theme
4. Return to chooser to switch

All navigation stays within the selected theme!

## Tips

💡 **Bookmark the chooser:** Save `hovedindex.html` for easy access

💡 **Share appropriately:** Send `-m.html` links to clients, `-n.html` to your team

💡 **Regenerate anytime:** Safe to run `--both` multiple times

💡 **Mix and match:** You can delete `-n.html` files if you only want Modern later

## Troubleshooting

**Q: Can I add a theme later?**
A: Yes! Run with `--theme nostalgia` or `--theme modern` to add missing files.

**Q: Both links not working?**
A: Make sure you used `--both` flag. Single theme mode doesn't create suffixed files.

**Q: How do I remove one theme?**
A: Delete all `*-n.html` files (for Nostalgia) or `*-m.html` files (for Modern).

**Q: Can I customize the chooser page?**
A: Yes! Edit the `_get_unified_hovedindex_template` method in `generate_index.py`.

## Advanced: Config File

You can't set `--both` in `config.yaml` (it's command-line only), but you can:

```yaml
html_generation:
  theme: "modern"  # Default if no --both or --theme flag
```

Then override with: `python generate_index.py --both`

---

**Enjoy having both themes available anytime! 🎨**
