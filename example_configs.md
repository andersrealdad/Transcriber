# Configuration Examples

Copy and paste these into your `config.yaml` for different use cases.

## 🎯 Use Case 1: Norwegian Podcast → English Summary

Perfect for: Norwegian content that you want summarized in English

```yaml
folders:
  input: "./input"
  output: ""

whisper:
  model_size: "large-v3"
  device: "cuda"
  compute_type: "float16"
  language: null  # Auto-detect Norwegian
  beam_size: 5
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"  # Good for podcasts

transcription:
  format: "txt"
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "llama3.2"
  generate_summary: true
  summary:
    style: "detailed"
    max_length: 500
    language: "en"  # English summary
    extract_topics: true
```

---

## ⚡ Use Case 2: Fast Batch Processing

Perfect for: Processing many files quickly with good quality

```yaml
folders:
  input: "./input"
  output: "./output"

whisper:
  model_size: "medium"  # Faster than large
  beam_size: 3  # Faster than 5
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: false  # Skip for speed

transcription:
  format: "txt"
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "llama3.2"
  summary:
    style: "concise"  # Shorter summaries
    max_length: 300
```

---

## 🎬 Use Case 3: Movie/Video Subtitles

Perfect for: Creating subtitle files

```yaml
folders:
  input: "./input"
  output: "./output"

whisper:
  model_size: "large-v3"
  language: null
  beam_size: 5
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"

transcription:
  format: "all"  # Creates .txt, .srt, .vtt, .json
  timestamps: true
  language_tag: true
  word_timestamps: true  # More precise timing

ollama:
  enabled: false  # No summary needed for subtitles
```

---

## 🎤 Use Case 4: Very Noisy Audio (Interviews, Field Recordings)

Perfect for: Poor quality audio with lots of background noise

```yaml
folders:
  input: "./input"
  output: ""

whisper:
  model_size: "large-v3"
  beam_size: 8  # Higher for difficult audio
  vad_filter: true
  vad_parameters:
    threshold: 0.4  # More sensitive
    min_speech_duration_ms: 200

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "both"  # Maximum denoising
    deepfilternet:
      attenuation_limit: 100  # Aggressive
  enhancement_filters:
    noise_reduction: 0.3  # Higher
    highpass: 300  # Remove more low-end
    normalize: true

transcription:
  format: "txt"
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "llama3.2"
  summary:
    style: "detailed"
    extract_topics: true
```

---

## 📚 Use Case 5: Academic Lectures

Perfect for: Long lectures with Q&A, need detailed notes

```yaml
folders:
  input: "./lectures"
  output: "./transcripts"

whisper:
  model_size: "large-v3"
  language: "en"  # Or "no" for Norwegian
  beam_size: 7
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"

transcription:
  format: "all"  # Get everything
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "llama3.1"  # Larger model for better comprehension
  summary:
    style: "detailed"
    max_length: 800  # Long summary
    extract_topics: true
    language: null  # Same as source
```

---

## 💼 Use Case 6: Business Meetings

Perfect for: Meeting recordings with action items

```yaml
folders:
  input: "./meetings"
  output: "./meeting_notes"

whisper:
  model_size: "large-v3"
  language: null
  beam_size: 5
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"

transcription:
  format: "txt"
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "mistral"  # Good for structured content
  summary:
    style: "bullet_points"  # Action items format
    max_length: 600
    extract_topics: true
```

---

## 📖 Use Case 7: PDF Document Processing Only

Perfect for: Just OCR, no audio transcription

```yaml
folders:
  input: "./documents"
  output: "./text_output"

whisper:
  model_size: "large-v3"  # Won't be used
  
audio:
  enhance: false  # Not processing audio

transcription:
  format: "txt"

ocr:
  enabled: true
  output_format: "md"  # Markdown output
  language: "eng+nor"  # Both languages
  dpi: 300

ollama:
  enabled: false  # No summary for documents

processing:
  skip_existing: true
  recursive: true
```

---

## 🌐 Use Case 8: Multilingual Content

Perfect for: Mixed English/Norwegian content

```yaml
folders:
  input: "./input"
  output: ""

whisper:
  model_size: "large-v3"
  language: null  # Auto-detect
  beam_size: 6
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"

transcription:
  format: "txt"
  timestamps: true
  language_tag: true  # Shows detected language

ollama:
  enabled: true
  model: "mistral"  # Excellent multilingual
  summary:
    style: "detailed"
    language: "en"  # Or "no" or null
    extract_topics: true
```

---

## 🎵 Use Case 9: Music with Vocals

Perfect for: Songs, music videos (extract lyrics)

```yaml
folders:
  input: "./music"
  output: "./lyrics"

whisper:
  model_size: "large-v3"
  language: null
  beam_size: 7
  vad_filter: false  # Don't filter silence in music

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"
    demucs:
      model: "htdemucs"
      extract: "vocals"  # Isolate vocals
  enhancement_filters:
    noise_reduction: 0  # Don't denoise music
    normalize: true

transcription:
  format: "txt"
  timestamps: true
  language_tag: true

ollama:
  enabled: false
```

---

## 🔬 Use Case 10: Research Interviews

Perfect for: Qualitative research, need verbatim transcripts

```yaml
folders:
  input: "./interviews"
  output: "./transcripts"

whisper:
  model_size: "large-v3"
  language: null
  beam_size: 10  # Maximum accuracy
  vad_filter: true
  vad_parameters:
    threshold: 0.3  # Catch soft speech
    min_speech_duration_ms: 100

audio:
  enhance: true
  ai_denoise:
    enabled: true
    method: "both"  # Maximum quality
  enhancement_filters:
    noise_reduction: 0.2
    normalize: true

transcription:
  format: "all"  # Get everything
  timestamps: true
  language_tag: true
  word_timestamps: true  # Detailed timing

ollama:
  enabled: true
  model: "llama3.1"
  summary:
    style: "detailed"
    max_length: 1000
    extract_topics: true
```

---

## 📱 Use Case 11: Voice Memos/Quick Notes

Perfect for: Personal recordings, quick transcriptions

```yaml
folders:
  input: "./voice_notes"
  output: ""  # Save next to original

whisper:
  model_size: "medium"  # Balance speed/quality
  language: null
  beam_size: 4
  vad_filter: true

audio:
  enhance: true
  ai_denoise:
    enabled: false  # Usually clean audio
  enhancement_filters:
    normalize: true

transcription:
  format: "txt"
  timestamps: false  # No timestamps for notes
  language_tag: true

ollama:
  enabled: true
  model: "llama3.2"
  summary:
    style: "concise"
    max_length: 200
```

---

## 🎬 Use Case 12: YouTube Video Processing

Perfect for: Downloaded YouTube videos

```yaml
folders:
  input: "./youtube"
  output: "./youtube_transcripts"

whisper:
  model_size: "large-v3"
  language: null  # Detect automatically
  beam_size: 5
  vad_filter: true

audio:
  formats: ["mp3", "wav", "m4a", "webm", "opus"]
  enhance: true
  ai_denoise:
    enabled: true
    method: "demucs"

transcription:
  format: "all"  # Get SRT for captions
  timestamps: true
  language_tag: true

ollama:
  enabled: true
  model: "llama3.2"
  summary:
    style: "detailed"
    max_length: 500
    extract_topics: true
    language: "en"
```

---

## 💡 Quick Config Swapping

Save different configs as:
- `config_fast.yaml`
- `config_quality.yaml`
- `config_podcast.yaml`

Then run:
```bash
./run_transcribe.sh config_podcast.yaml
```

---

## 🔄 Config Modifications Quick Reference

### Make it Faster
```yaml
whisper.model_size: "medium"  # Instead of large-v3
whisper.beam_size: 3  # Instead of 5
audio.ai_denoise.enabled: false
ollama.enabled: false
```

### Make it Better Quality
```yaml
whisper.model_size: "large-v3"
whisper.beam_size: 10
audio.ai_denoise.method: "both"
ollama.model: "llama3.1"
```

### Reduce GPU Memory
```yaml
whisper.model_size: "medium"  # or "small"
whisper.compute_type: "int8"  # Instead of float16
```

### More Aggressive Denoising
```yaml
audio.ai_denoise.method: "both"
audio.ai_denoise.deepfilternet.attenuation_limit: 100
audio.enhancement_filters.noise_reduction: 0.4
```

---

**Copy the config that matches your use case, or mix and match settings!**