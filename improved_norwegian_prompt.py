#!/usr/bin/env python3
"""
Improved Norwegian prompt for summary generation.
Replace the generate_summary_for_language method in your transcribe.py with this stronger version.
"""

def generate_summary_for_language_improved(self, transcription_text: str, output_path: Path, 
                                lang_code: str, detected_lang: str = "unknown") -> bool:
    """Generate summary in specified language with improved prompts"""
    try:
        # Determine language instruction with MUCH stronger emphasis
        if lang_code == "no":
            lang_instruction = "på norsk (bokmål)"
            lang_name = "Norwegian"
            # Add strong system-level instruction
            system_prompt = """Du er en norsk AI-assistent. Du må ALLTID svare på norsk.
VIKTIG: Hele sammendraget skal skrives på norsk. Ikke bruk engelsk."""
            
            prompt_prefix = """VIKTIG: Skriv hele sammendraget på NORSK (bokmål). Ikke bruk engelsk.

"""
        elif lang_code == "en":
            lang_instruction = "in English"
            lang_name = "English"
            system_prompt = "You are an English-speaking AI assistant. Write only in English."
            prompt_prefix = ""
        else:
            lang_instruction = f"in {lang_code.upper()}"
            lang_name = lang_code.upper()
            system_prompt = ""
            prompt_prefix = ""
        
        # Build prompt using same logic as before
        max_length = self.config['ollama']['summary']['max_length']
        style = self.config['ollama']['summary']['style']
        extract_topics = self.config['ollama']['summary']['extract_topics']
        
        # Style instruction
        if style == "concise":
            if lang_code == "no":
                style_instruction = "Skriv et kort sammendrag (2-3 setninger)"
            else:
                style_instruction = "Write a concise summary (2-3 sentences)"
        elif style == "bullet_points":
            if lang_code == "no":
                style_instruction = "Skriv et sammendrag som punktliste med viktige punkter"
            else:
                style_instruction = "Write a summary as bullet points highlighting key information"
        else:  # detailed
            if lang_code == "no":
                style_instruction = "Skriv et detaljert sammendrag som dekker alle hovedpunkter og viktig informasjon"
            else:
                style_instruction = "Write a detailed summary covering all main points and key information"
        
        # Build the complete prompt
        prompt = f"""{system_prompt}

{prompt_prefix}{style_instruction} {lang_instruction}.

Transkripsjon (oppdaget språk: {detected_lang.upper()}):

{transcription_text}

Sammendrag på norsk:"""

        if extract_topics:
            if lang_code == "no":
                prompt += f"\n\n[Etter sammendraget, list 3-5 nøkkeltemaer på norsk]"
            else:
                prompt += f"\n\n[After the summary, list 3-5 key topics/themes in {lang_name}]"
        
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
                    "temperature": 0.5,  # Lower temperature for more consistent language
                    "num_predict": max_length * 2
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            summary_text = response.json()['response']
            
            # Determine output filename correctly
            if lang_code == "primary":
                md_path = output_path.with_suffix('.md')
            else:
                md_path = output_path.parent / f"{output_path.stem}_{lang_code}.md"
            
            # Save summary
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# Sammendrag: {output_path.stem}\n\n" if lang_code == "no" else f"# Summary: {output_path.stem}\n\n")
                f.write(f"**Generert av:** {model}\n\n")
                f.write(f"**Språk:** {lang_name}\n\n")
                f.write(f"**Kildespråk:** {detected_lang.upper()}\n\n")
                f.write(f"---\n\n")
                f.write(summary_text.strip())
                f.write("\n\n---\n\n")
                if lang_code == "no":
                    f.write(f"*Generert fra transkripsjon: {output_path.with_suffix('.txt').name}*\n")
                else:
                    f.write(f"*Generated from transcription: {output_path.with_suffix('.txt').name}*\n")
            
            self.logger.info(f"Generated {lang_name} summary: {md_path}")
            return True
        else:
            self.logger.error(f"Ollama API error for {lang_name}: {response.status_code}")
            return False
            
    except Exception as e:
        self.logger.error(f"Summary generation failed for {lang_name}: {e}")
        return False


# Instructions for implementing:
print("""
To fix Norwegian summary generation:

1. Replace config.yaml with the corrected version
2. Update the generate_summary_for_language method in transcribe.py with this improved version
3. Consider switching to a better Norwegian model like:
   - llama3.2:3b or llama3.1:8b
   - mistral:7b
   
The key improvements:
- Stronger Norwegian instructions in the prompt
- System-level instruction in Norwegian
- Lower temperature (0.5 instead of 0.7) for more consistent language adherence
- Norwegian labels in the output markdown
""")
