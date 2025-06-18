#!/usr/bin/env python3
"""
Gemini Pro TTS CLI - MVP Implementation (New SDK)
Converts text files to WAV audio using Gemini 2.5 Pro Preview TTS
Uses the new google-genai SDK (v1.0+)
"""

import argparse
import os
import sys
import wave
import io
import asyncio
from pathlib import Path
from typing import List, Optional

from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_STYLE = "reads aloud in a high school girl, vivacious, fresh, lively, fast-talking and smooth, Japanese anime-style voice:"
DEFAULT_VOICE = "Zephyr"
DEFAULT_MODEL = "gemini-2.5-pro-preview-tts"
MAX_TOKENS = 32000


def main():
    parser = argparse.ArgumentParser(
        description="Convert text files to WAV audio using Gemini TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python gemini_tts_cli.py -i script.txt -o result.wav --style "whispering, mysterious tone:" --voice Kore
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Input UTF-8 text file to convert"
    )
    
    parser.add_argument(
        "--output", "-o", 
        required=True,
        type=Path,
        help="Output WAV file path"
    )
    
    parser.add_argument(
        "--style", "-s",
        default=DEFAULT_STYLE,
        help=f"Style instruction prefix (default: {DEFAULT_STYLE[:50]}...)"
    )
    
    parser.add_argument(
        "--voice", "-v",
        default=DEFAULT_VOICE,
        help=f"Voice name from Gemini TTS (default: {DEFAULT_VOICE})"
    )
    
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        help=f"TTS model name (default: {os.getenv('GEMINI_MODEL', DEFAULT_MODEL)})"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        converter = GeminiTTSConverter(
            model=args.model,
            voice=args.voice,
            style=args.style,
            verbose=args.verbose
        )
        
        asyncio.run(converter.convert_text_file_async(args.input, args.output))
        print(f"Successfully converted {args.input} to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


class GeminiTTSConverter:
    def __init__(self, model: str, voice: str, style: str, verbose: bool = False):
        self.model = model
        self.voice = voice
        self.style = style
        self.verbose = verbose
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=api_key)
    
    async def convert_text_file_async(self, input_path: Path, output_path: Path) -> None:
        """Convert text file to WAV using async processing"""
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        text = input_path.read_text(encoding="utf-8")
        chunks = self._split_text(text)
        
        audio_buffers = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks, 1):
            if self.verbose:
                print(f"Processing chunk {i}/{total_chunks}...")
            else:
                print(f"Chunk {i}/{total_chunks} ... ", end="", flush=True)
                
            audio_data = await self._generate_audio_async(chunk)
            audio_buffers.append(audio_data)
            
            if not self.verbose:
                print("done")
        
        self._save_wav(audio_buffers, output_path)
    
    def convert_text_file(self, input_path: Path, output_path: Path) -> None:
        """Synchronous wrapper for convert_text_file_async"""
        asyncio.run(self.convert_text_file_async(input_path, output_path))
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks for processing"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Rough estimation: 1 token ~= 4 characters
            estimated_tokens = len(current_chunk + paragraph) // 4
            
            if estimated_tokens > MAX_TOKENS and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks if chunks else [text]
    
    async def _generate_audio_async(self, text: str) -> bytes:
        """Generate audio from text using new SDK (async)"""
        styled_text = f"{self.style} {text}" if self.style else text
        
        try:
            # Use the new google-genai SDK
            response = await asyncio.to_thread(
                self._generate_audio_sync, styled_text
            )
            return response
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {e}")
    
    def _generate_audio_sync(self, styled_text: str) -> bytes:
        """Synchronous audio generation for thread execution"""
        try:
            # Configure for TTS generation
            config = GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config={
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self.voice
                        }
                    }
                }
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[styled_text],
                config=config
            )
            
            # Extract audio data from response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            if part.inline_data.mime_type.startswith('audio/'):
                                return part.inline_data.data
            
            # Alternative: check for direct audio_data attribute
            if hasattr(response, 'audio_data') and response.audio_data:
                return response.audio_data
                
            # Alternative: check in parts directly
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'audio_data'):
                        return part.audio_data
                        
            raise RuntimeError("No audio data found in response")
            
        except Exception as e:
            if self.verbose:
                print(f"Debug: Response structure: {dir(response) if 'response' in locals() else 'No response'}")
            raise RuntimeError(f"API call failed: {e}")
    
    def _save_wav(self, audio_buffers: List[bytes], output_path: Path) -> None:
        """Save audio buffers to WAV file"""
        if not audio_buffers:
            raise ValueError("No audio data to save")
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(str(output_path), 'wb') as wav_file:
            # WAV parameters: 16-bit PCM, 24kHz, mono (Gemini TTS standard)
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(24000)  # 24kHz
            
            for audio_data in audio_buffers:
                if isinstance(audio_data, str):
                    # If audio_data is base64 string, decode it
                    import base64
                    audio_data = base64.b64decode(audio_data)
                wav_file.writeframes(audio_data)


if __name__ == "__main__":
    main()