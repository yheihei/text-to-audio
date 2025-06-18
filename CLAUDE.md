# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 応答のルール

日本語で応答すること

## タスク完了時

下記コマンドを叩くこと

```
say "終わったよ~"
```

## Project Overview

This is a Gemini Pro TTS CLI tool that converts text files to high-quality WAV audio using Google's Gemini 2.5 Pro Preview TTS API. The project is a single-file Python CLI application with Japanese language support.

## Architecture

- **Main entry point**: `gemini_tts_cli.py` - Contains both CLI interface and TTS conversion logic
- **Core class**: `GeminiTTSConverter` - Handles API interaction, text chunking, and audio processing
- **Text processing**: Automatic text splitting for 32k token limit with paragraph-based chunking
- **Audio output**: WAV format (PCM 16-bit, 24kHz, mono)

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env to add GEMINI_API_KEY=your-api-key
```

### Running the CLI
```bash
# Basic usage
python gemini_tts_cli.py -i input.txt -o output.wav

# With options
python gemini_tts_cli.py --input script.txt --output result.wav --style "whispering, mysterious tone:" --voice Kore --verbose
```

### Testing
Use `sample.txt` as test input for development and testing.

## Key Configuration

- **Environment**: Requires `GEMINI_API_KEY` in environment or `.env` file  
- **Model**: Default is `gemini-2.5-pro-preview-tts`
- **Voice**: Default is "Zephyr" (30 voices available)
- **Token limit**: 32,000 tokens with automatic text chunking
- **Audio format**: Fixed to WAV PCM 16-bit, 24kHz, mono

## Important Implementation Details

- Text chunking uses rough estimation (1 token ≈ 4 characters)
- Multiple audio chunks are concatenated into single WAV file
- Error handling for API failures, missing files, and missing API keys
- Progress indication for multi-chunk processing
- UTF-8 text file support with Japanese language content