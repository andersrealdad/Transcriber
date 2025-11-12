#!/usr/bin/env python3
"""
Transcription and OCR Processing Script
Processes audio files with Faster-Whisper and PDFs with OCR
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import List, Optional, Dict
import subprocess
import tempfile
import requests
import json

from faster_whisper import WhisperModel
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm


class TranscriptionProcessor:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the processor with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        log_level = getattr(logging, self.config['processing']['log_level'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Whisper model
        self.logger.info("Loading Faster-Whisper model...")
        self.model = WhisperModel(
            self.config['whisper']['model_size'],
            device=self.config['whisper']['device'],
            compute_type=self.config['whisper']['compute_type']
        )
        self.logger.info("Model loaded successfully!")
        
        # Setup paths
        self.input_folder = Path(self.config['folders']['input'])
        self.output_folder = Path(self.config['folders']['output']) if self.config['folders']['output'] else None
        
        if not self.input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")
        
        # Check Ollama availability
        self.ollama_available = False
        if self.config['ollama']['enabled']:
            self.ollama_available = self._check_ollama()
        
        # Check if DeepFilterNet is actually available
        self.deepfilternet_available = self._check_deepfilternet()

    def _check_deepfilternet(self) -> bool:
        """Check if DeepFilterNet is actually importable and usable"""
        try:
            import deepfilternet
            from df.enhance import enhance, init_df
            self.logger.info("DeepFilterNet is available")
            return True
        except ImportError as e:
            self.logger.warning(f"DeepFilterNet not available: {e}")
            return False

    def _check_ollama(self) -> bool:
        """Check if Ollama is available and model exists"""
        try:
            api_url = self.config['ollama']['api_url']
            # Check if Ollama is running
            response = requests.get(f"{api_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                target_model = self.config['ollama']['model']
                
                # Check if target model exists (handle version tags)
                model_found = any(target_model in name for name in model_names)
                
                if model_found:
                    self.logger.info(f"Ollama available with model: {target_model}")
                    return True
                else:
                    self.logger.warning(f"Ollama model '{target_model}' not found.")
                    self.logger.info(f"Available models: {', '.join(model_names)}")
                    self.logger.info(f"Install with: ollama pull {target_model}")
                    return False
            return False
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            return False

    def ai_denoise(self, input_path: Path) -> Optional[Path]:
        """Apply AI-based denoising using Demucs and/or DeepFilterNet"""
        if not self.config['audio']['ai_denoise']['enabled']:
            return None
        
        method = self.config['audio']['ai_denoise']['method']
        
        if method == "none":
            return None
        
        # Skip DeepFilterNet if not available
        if method in ["deepfilternet", "both"] and not self.deepfilternet_available:
            self.logger.warning("DeepFilterNet requested but not available, skipping")
            if method == "deepfilternet":
                return None
            method = "demucs"  # Fall back to demucs if "both" was requested
        
        try:
            # Create temp file for denoised audio
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            current_path = input_path
            
            # Apply Demucs (vocal separation)
            if method in ["demucs", "both"]:
                self.logger.info(f"Applying Demucs denoising to {input_path.name}...")
                demucs_path = self._apply_demucs(current_path)
                if demucs_path:
                    current_path = demucs_path
                else:
                    self.logger.warning("Demucs failed, continuing without it")
            
            # Apply DeepFilterNet (noise suppression)
            if method in ["deepfilternet", "both"] and self.deepfilternet_available:
                self.logger.info(f"Applying DeepFilterNet to {input_path.name}...")
                dfnet_path = self._apply_deepfilternet(current_path)
                if dfnet_path:
                    # Clean up intermediate file if we used Demucs
                    if method == "both" and current_path != input_path:
                        current_path.unlink()
                    current_path = dfnet_path
                else:
                    self.logger.warning("DeepFilterNet failed")
            
            # Copy final result to temp_path
            if current_path != input_path:
                import shutil
                shutil.copy(current_path, temp_path)
                # Clean up intermediate file
                if current_path != input_path:
                    current_path.unlink()
                return temp_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"AI denoising error: {e}")
            return None

    def _apply_demucs(self, input_path: Path) -> Optional[Path]:
        """Apply Demucs for vocal separation"""
        try:
            model = self.config['audio']['ai_denoise']['demucs']['model']
            extract = self.config['audio']['ai_denoise']['demucs']['extract']
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            # Run Demucs
            cmd = [
                'demucs',
                '--two-stems', extract,
                '-n', model,
                '--out', output_dir,
                str(input_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the extracted vocals file
                stem_path = Path(output_dir) / model / input_path.stem / f"{extract}.wav"
                if stem_path.exists():
                    # Copy to temp location
                    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    temp_path = Path(temp_file.name)
                    temp_file.close()
                    
                    import shutil
                    shutil.copy(stem_path, temp_path)
                    
                    # Clean up Demucs output
                    shutil.rmtree(output_dir)
                    
                    self.logger.info(f"Demucs completed: extracted {extract}")
                    return temp_path
            else:
                self.logger.error(f"Demucs error: {result.stderr}")
            
            return None
            
        except FileNotFoundError:
            self.logger.error("Demucs not installed. Install with: pip install demucs")
            return None
        except Exception as e:
            self.logger.error(f"Demucs error: {e}")
            return None

    def _apply_deepfilternet(self, input_path: Path) -> Optional[Path]:
        """Apply DeepFilterNet for noise suppression using Python API"""
        try:
            from df.enhance import enhance, init_df
            from df.io import resample
            import torch
            import soundfile as sf
            
            atten_limit = self.config['audio']['ai_denoise']['deepfilternet']['attenuation_limit']
            
            # Create temp output file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            # Initialize DeepFilterNet model
            model, df_state, _ = init_df()
            
            # Load audio
            audio, sr = sf.read(str(input_path))
            
            # Resample if needed
            if sr != df_state.sr():
                audio = resample(audio, sr, df_state.sr())
            
            # Enhance
            enhanced = enhance(model, df_state, audio, atten_lim_db=atten_limit)
            
            # Save
            sf.write(str(temp_path), enhanced, df_state.sr())
            
            self.logger.info("DeepFilterNet completed")
            return temp_path
                
        except ImportError:
            self.logger.error("DeepFilterNet not properly installed")
            return None
        except Exception as e:
            self.logger.error(f"DeepFilterNet error: {e}")
            return None

    def enhance_audio(self, input_path: Path) -> Optional[Path]:
        """Enhance audio quality using ffmpeg filters"""
        if not self.config['audio']['enhance']:
            return None
        
        try:
            # Create temporary enhanced audio file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            # Build ffmpeg filter chain
            filters = []
            enh = self.config['audio']['enhancement_filters']
            
            if enh.get('highpass'):
                filters.append(f"highpass=f={enh['highpass']}")
            
            if enh.get('noise_reduction') and enh['noise_reduction'] > 0:
                # Convert 0.0-1.0 scale to dB scale (-90 to -20)
                # 0.0 -> -90dB (no reduction), 1.0 -> -20dB (max reduction)
                nf_db = -90 + (enh['noise_reduction'] * 70)
                filters.append(f"afftdn=nf={nf_db}")
            
            if enh.get('normalize'):
                filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            
            filter_str = ",".join(filters) if filters else "anull"
            
            # Run ffmpeg
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-af', filter_str,
                '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                str(temp_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.warning(f"Audio enhancement failed: {result.stderr}")
                return None
            
            self.logger.info(f"FFmpeg enhancement completed")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error enhancing audio: {e}")
            return None

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to [HH:MM:SS] format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"

    def transcribe_audio(self, audio_path: Path) -> Optional[Dict]:
        """Transcribe audio file using Faster-Whisper"""
        
        # Check if multi-pass is enabled
        if self.config['multi_pass']['enabled']:
            return self.multi_pass_transcribe(audio_path)
        
        # Standard single-pass transcription
        return self._single_pass_transcribe(audio_path, 
                                           ai_denoise_method=self.config['audio']['ai_denoise']['method'])

    def _single_pass_transcribe(self, audio_path: Path, ai_denoise_method: str = None) -> Optional[Dict]:
        """Single pass transcription with specified denoising method"""
        self.logger.info(f"Transcribing: {audio_path.name}")
        
        # Temporarily override AI denoise method if specified
        original_method = self.config['audio']['ai_denoise']['method']
        if ai_denoise_method:
            self.config['audio']['ai_denoise']['method'] = ai_denoise_method
        
        # Apply AI denoising first
        ai_denoised_path = self.ai_denoise(audio_path)
        
        # Then apply FFmpeg enhancement
        enhanced_path = self.enhance_audio(ai_denoised_path if ai_denoised_path else audio_path)
        
        # Restore original method
        self.config['audio']['ai_denoise']['method'] = original_method
        
        # Determine which file to process
        if enhanced_path:
            process_path = enhanced_path
        elif ai_denoised_path:
            process_path = ai_denoised_path
        else:
            process_path = audio_path
        
        try:
            # Get VAD parameters from config and create VadOptions
            vad_config = self.config['whisper'].get('vad_parameters', {})
            
            # Build VAD options with only supported parameters
            # Remove 'threshold' as it's not supported in current faster-whisper
            vad_options = {}
            if 'min_speech_duration_ms' in vad_config:
                vad_options['min_speech_duration_ms'] = vad_config['min_speech_duration_ms']
            if 'min_silence_duration_ms' in vad_config:
                vad_options['min_silence_duration_ms'] = vad_config['min_silence_duration_ms']
            
            # Get processing duration for logging
            duration_result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(process_path)],
                capture_output=True, text=True
            )
            if duration_result.returncode == 0:
                duration_secs = float(duration_result.stdout.strip())
                hours = int(duration_secs // 3600)
                minutes = int((duration_secs % 3600) // 60)
                seconds = int(duration_secs % 60)
                self.logger.info(f"Processing audio with duration {hours:02d}:{minutes:02d}:{seconds:02d}.{int((duration_secs % 1) * 1000):03d}")
            
            # Transcribe
            segments, info = self.model.transcribe(
                str(process_path),
                language=self.config['whisper']['language'],
                beam_size=self.config['whisper']['beam_size'],
                vad_filter=self.config['whisper']['vad_filter'],
                vad_parameters=vad_options if vad_options else None,
                word_timestamps=self.config['transcription']['word_timestamps']
            )
            
            self.logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            # Collect segments
            results = {
                'language': info.language,
                'language_probability': info.language_probability,
                'segments': [],
                'full_text': '',
                'audio_processing': {
                    'ai_denoise': ai_denoise_method if ai_denoise_method and ai_denoised_path else 'None',
                    'ffmpeg_enhance': 'Yes' if enhanced_path else 'No',
                    'normalize': 'Yes' if self.config['audio']['enhancement_filters'].get('normalize') else 'No'
                }
            }
            
            full_text_parts = []
            for segment in segments:
                results['segments'].append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text_parts.append(segment.text.strip())
            
            results['full_text'] = ' '.join(full_text_parts)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Transcription failed for {audio_path.name}: {e}")
            return None
        finally:
            # Clean up temporary files
            if enhanced_path and enhanced_path.exists():
                enhanced_path.unlink()
            if ai_denoised_path and ai_denoised_path.exists():
                ai_denoised_path.unlink()

    def multi_pass_transcribe(self, audio_path: Path) -> Optional[Dict]:
        """Transcribe with multiple strategies and merge best results"""
        self.logger.info(f"Starting multi-pass transcription: {audio_path.name}")
        
        strategies = self.config['multi_pass']['strategies']
        all_results = {}
        
        # Filter out DeepFilterNet strategies if not available
        available_strategies = []
        for strategy in strategies:
            if 'deepfilternet' in strategy and not self.deepfilternet_available:
                self.logger.warning(f"Skipping strategy '{strategy}' - DeepFilterNet not available")
                continue
            available_strategies.append(strategy)
        
        if not available_strategies:
            self.logger.error("No available transcription strategies")
            return None
        
        # Transcribe with each strategy
        for strategy in available_strategies:
            self.logger.info(f"  Pass {len(all_results)+1}/{len(available_strategies)}: {strategy}")
            result = self._single_pass_transcribe(audio_path, ai_denoise_method=strategy)
            
            if result:
                all_results[strategy] = result
                
                # Save individual transcription if configured
                if self.config['multi_pass']['keep_individual']:
                    output_path = self.get_output_path(audio_path)
                    individual_path = output_path.with_stem(f"{output_path.stem}_{strategy}")
                    self._save_txt(result, individual_path.with_suffix('.txt'))
        
        if not all_results:
            self.logger.error("All transcription strategies failed")
            return None
        
        # If only one succeeded, return it
        if len(all_results) == 1:
            return list(all_results.values())[0]
        
        # Merge results using LLM if enabled
        if self.config['multi_pass']['llm_merge'] and self.ollama_available:
            merged_result = self._llm_merge_transcriptions(all_results, audio_path)
            if merged_result:
                return merged_result
        
        # Fallback: return the one with highest language probability
        best_strategy = max(all_results.items(), 
                          key=lambda x: x[1]['language_probability'])[0]
        self.logger.info(f"Using best single result: {best_strategy}")
        
        result = all_results[best_strategy]
        result['multi_pass_info'] = {k: v['language_probability'] 
                                     for k, v in all_results.items()}
        return result

    def _llm_merge_transcriptions(self, all_results: Dict, audio_path: Path) -> Optional[Dict]:
        """Use LLM to intelligently merge multiple transcriptions"""
        self.logger.info("Merging transcriptions with LLM...")
        
        try:
            # Prepare comparison text
            comparison = f"Multiple transcriptions of: {audio_path.name}\n\n"
            
            for strategy, result in all_results.items():
                comparison += f"=== Strategy: {strategy} (confidence: {result['language_probability']:.1%}) ===\n"
                for seg in result['segments']:
                    timestamp = self.format_timestamp(seg['start'])
                    comparison += f"{timestamp} {seg['text']}\n"
                comparison += "\n"
            
            # Ask LLM to create best version
            prompt = f"""You are analyzing multiple transcriptions of the same audio. 
Your task is to create the BEST POSSIBLE transcription by:
1. Comparing segments at each timestamp
2. Choosing the most accurate text (best grammar, most sensible content)
3. Maintaining exact timestamps

{comparison}

Output ONLY the final transcription in this format:
[HH:MM:SS] text

Do not add explanations or comments."""

            api_url = self.config['ollama']['api_url']
            model = self.config['ollama']['model']
            
            response = requests.post(
                f"{api_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}  # Low temp for accuracy
                },
                timeout=300
            )
            
            if response.status_code == 200:
                merged_text = response.json()['response']
                
                # Parse LLM output back into segments
                import re
                pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]\s*(.+?)(?=\[|$)'
                matches = re.finditer(pattern, merged_text, re.DOTALL)
                
                segments = []
                for match in matches:
                    h, m, s, text = match.groups()
                    start_time = int(h) * 3600 + int(m) * 60 + int(s)
                    segments.append({
                        'start': start_time,
                        'end': start_time + 5,  # Approximate
                        'text': text.strip()
                    })
                
                if segments:
                    # Use metadata from best single result
                    best_result = max(all_results.values(), 
                                    key=lambda x: x['language_probability'])
                    
                    return {
                        'language': best_result['language'],
                        'language_probability': best_result['language_probability'],
                        'segments': segments,
                        'full_text': ' '.join(s['text'] for s in segments),
                        'audio_processing': best_result['audio_processing'],
                        'multi_pass_merged': True,
                        'strategies_used': list(all_results.keys())
                    }
            
            self.logger.warning("LLM merge failed, using fallback")
            return None
            
        except Exception as e:
            self.logger.error(f"LLM merge error: {e}")
            return None

    def _save_txt(self, results: Dict, output_path: Path):
        """Helper to save just the text output"""
        with open(output_path, 'w', encoding='utf-8') as f:
            if self.config['transcription']['timestamps']:
                for segment in results['segments']:
                    if self.config['transcription']['timestamp_format'] == 'timecode':
                        timestamp = self.format_timestamp(segment['start'])
                    else:
                        timestamp = f"[{segment['start']:.2f}s]"
                    f.write(f"{timestamp} {segment['text']}\n")
            else:
                f.write(results['full_text'])

    def save_transcription(self, results: Dict, output_path: Path):
        """Save transcription results in configured formats"""
        format_type = self.config['transcription']['format']
        
        # Save TXT format (always, as base)
        txt_path = output_path.with_suffix('.txt')
        self._save_txt(results, txt_path)
        self.logger.info(f"Saved transcription: {txt_path}")
        
        # Save additional formats if requested
        if format_type in ['srt', 'all']:
            self._save_srt(results, output_path.with_suffix('.srt'))
        
        if format_type in ['vtt', 'all']:
            self._save_vtt(results, output_path.with_suffix('.vtt'))
        
        if format_type in ['json', 'all']:
            self._save_json(results, output_path.with_suffix('.json'))
        
        # Generate Ollama summary if enabled
        if self.ollama_available and self.config['ollama']['generate_summary']:
            self.generate_summary(results, output_path)

    def _save_srt(self, results: Dict, output_path: Path):
        """Save as SRT subtitle format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(results['segments'], 1):
                start = self._format_srt_time(segment['start'])
                end = self._format_srt_time(segment['end'])
                f.write(f"{i}\n{start} --> {end}\n{segment['text']}\n\n")
        self.logger.info(f"Saved SRT: {output_path}")

    def _save_vtt(self, results: Dict, output_path: Path):
        """Save as WebVTT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in results['segments']:
                start = self._format_vtt_time(segment['start'])
                end = self._format_vtt_time(segment['end'])
                f.write(f"{start} --> {end}\n{segment['text']}\n\n")
        self.logger.info(f"Saved VTT: {output_path}")

    def _save_json(self, results: Dict, output_path: Path):
        """Save as JSON with full metadata"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved JSON: {output_path}")

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_vtt_time(self, seconds: float) -> str:
        """Format time for VTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def generate_summary(self, results: Dict, output_path: Path):
        """Generate AI summary using Ollama"""
        try:
            full_text = results['full_text']
            
            # Check if text is long enough for summary
            if len(full_text.split()) < 50:
                self.logger.info("Text too short for summary")
                return
            
            # Build prompt based on config
            max_length = self.config['ollama']['summary']['max_length']
            style = self.config['ollama']['summary']['style']
            extract_topics = self.config['ollama']['summary']['extract_topics']
            lang = self.config['ollama']['summary']['language']
            
            # Language instruction
            if lang:
                lang_instruction = f"in {lang.upper()}"
            else:
                lang_instruction = f"in the same language as the transcription ({results.get('language', 'unknown').upper()})"
            
            # Style instruction
            if style == "concise":
                style_instruction = "Write a concise summary (2-3 sentences)"
            elif style == "bullet_points":
                style_instruction = "Write a summary as bullet points highlighting key information"
            else:  # detailed
                style_instruction = "Write a detailed summary covering all main points and key information"
            
            prompt = f"""{style_instruction} {lang_instruction}.

Transcription (detected language: {results.get('language', 'unknown').upper()}):

{full_text}

Summary:"""

            if extract_topics:
                prompt += "\n\n[After the summary, list 3-5 key topics/themes]"
            
            # Call Ollama API
            api_url = self.config['ollama']['api_url']
            model = self.config['ollama']['model']
            
            response = requests.post(
                f"{api_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": max_length * 2  # Rough token estimate
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                summary_text = response.json()['response']
                
                # Save summary as markdown
                md_path = output_path.with_suffix('.md')
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Summary: {output_path.stem}\n\n")
                    
                    # Add metadata
                    f.write(f"**Generated by:** {model}\n\n")
                    f.write(f"**Language:** {results.get('language', 'unknown').upper()}\n\n")
                    f.write(f"---\n\n")
                    
                    # Add summary
                    f.write(summary_text.strip())
                    f.write("\n\n---\n\n")
                    f.write(f"*Generated from transcription: {output_path.with_suffix('.txt').name}*\n")
                
                self.logger.info(f"Summary saved: {md_path}")
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timeout (model might be busy)")
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")

    def ocr_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF using OCR"""
        if not self.config['ocr']['enabled']:
            return None
        
        self.logger.info(f"OCR processing: {pdf_path.name}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.config['ocr']['dpi']
            )
            
            # OCR each page
            text_parts = []
            for i, image in enumerate(tqdm(images, desc=f"OCR {pdf_path.name}"), 1):
                text = pytesseract.image_to_string(
                    image,
                    lang=self.config['ocr']['language']
                )
                text_parts.append(f"--- Page {i} ---\n{text}\n")
            
            full_text = "\n".join(text_parts)
            return full_text
            
        except Exception as e:
            self.logger.error(f"OCR failed for {pdf_path.name}: {e}")
            return None

    def save_ocr_result(self, text: str, output_path: Path):
        """Save OCR result in configured format"""
        format_type = self.config['ocr']['output_format']
        
        if format_type == 'txt':
            with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
        
        elif format_type == 'md':
            with open(output_path.with_suffix('.md'), 'w', encoding='utf-8') as f:
                f.write(f"# OCR Result: {output_path.stem}\n\n")
                f.write(text)
        
        elif format_type == 'json':
            import json
            with open(output_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                json.dump({'text': text}, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved OCR result: {output_path}")

    def get_output_path(self, input_path: Path, suffix: str = None) -> Path:
        """Determine output path based on configuration"""
        if self.output_folder:
            # Use output folder
            self.output_folder.mkdir(parents=True, exist_ok=True)
            
            # Preserve folder structure if enabled
            if self.config['processing']['preserve_structure']:
                # Get relative path from input folder
                try:
                    rel_path = input_path.relative_to(self.input_folder)
                    output_path = self.output_folder / rel_path.parent / input_path.name
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                except ValueError:
                    # If file is not in input folder, just use filename
                    output_path = self.output_folder / input_path.name
            else:
                output_path = self.output_folder / input_path.name
        else:
            # Use same folder as input
            output_path = input_path
        
        if suffix:
            output_path = output_path.with_suffix(suffix)
        
        return output_path

    def should_skip(self, output_path: Path) -> bool:
        """Check if file should be skipped"""
        if not self.config['processing']['skip_existing']:
            return False
        
        return output_path.exists()

    def process_all(self):
        """Process all audio and PDF files in input folder"""
        # Find all files
        audio_files = []
        pdf_files = []
        
        audio_extensions = [f".{ext}" for ext in self.config['audio']['formats']]
        
        if self.config['processing']['recursive']:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in self.input_folder.glob(pattern):
            if file_path.is_file():
                if file_path.suffix.lower() in audio_extensions:
                    audio_files.append(file_path)
                elif file_path.suffix.lower() == '.pdf':
                    pdf_files.append(file_path)
        
        self.logger.info(f"Found {len(audio_files)} audio files and {len(pdf_files)} PDF files")
        
        # Process audio files
        for audio_file in tqdm(audio_files, desc="Transcribing audio"):
            output_path = self.get_output_path(audio_file)
            
            if self.should_skip(output_path.with_suffix('.txt')):
                self.logger.info(f"Skipping existing: {audio_file.name}")
                continue
            
            results = self.transcribe_audio(audio_file)
            if results:
                self.save_transcription(results, output_path)
        
        # Process PDF files
        for pdf_file in tqdm(pdf_files, desc="OCR processing PDFs"):
            output_path = self.get_output_path(pdf_file)
            
            if self.should_skip(output_path.with_suffix('.txt')):
                self.logger.info(f"Skipping existing: {pdf_file.name}")
                continue
            
            text = self.ocr_pdf(pdf_file)
            if text:
                self.save_ocr_result(text, output_path)
        
        self.logger.info("Processing complete!")


def main():
    """Main entry point"""
    config_file = "config.yaml"
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    try:
        processor = TranscriptionProcessor(config_file)
        processor.process_all()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
