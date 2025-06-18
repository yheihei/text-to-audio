# Gemini Pro TTS CLI

Gemini 2.5 Pro Preview TTS を使用してテキストファイルを音声（WAV）に変換する CLI ツールです。

## 機能

- テキストファイルを高品質な WAV 音声に変換
- 30種類の音声から選択可能
- スタイル指示によるカスタマイズ
- 長いテキストの自動分割処理（32k token制限対応）
- 進捗表示とエラーハンドリング

## インストール

```bash
# 依存関係をインストール（新しいSDK使用）
pip install -r requirements.txt

# 環境変数ファイルを作成
cp .env.example .env
# .env ファイルを編集してAPIキーを設定
# GEMINI_API_KEY=your-actual-api-key-here
```

**注意**: このバージョンは新しい `google-genai` SDK (v1.0+) を使用しています。古い `google-generativeai` は非推奨です。

## 使用方法

### 基本的な使用法

```bash
python gemini_tts_cli.py -i input.txt -o output.wav
```

### オプション付き

```bash
python gemini_tts_cli.py \
  --input script.txt \
  --output result.wav \
  --style "囁くような、神秘的なトーン:" \
  --voice Kore \
  --verbose
```

## パラメータ

| パラメータ | 必須 | 説明 | デフォルト値 |
|-----------|------|------|-------------|
| `--input, -i` | ○ | 入力テキストファイル (UTF-8) | - |
| `--output, -o` | ○ | 出力WAVファイル | - |
| `--style, -s` | - | スタイル指示文 | 高校生女子のアニメ風音声 |
| `--voice, -v` | - | 音声名 (30種類から選択) | Zephyr |
| `--model` | - | TTS モデル名 | gemini-2.5-pro-preview-tts |
| `--verbose` | - | 詳細ログ表示 | false |

## 音声オプション

利用可能な音声（一部）:
- Zephyr（デフォルト）
- Kore
- その他28種類の音声

詳細は [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs/speech-generation) を参照してください。

## 技術仕様

- **出力形式**: WAV (PCM 16-bit, 24kHz, モノラル)
- **対応環境**: Python 3.9+, macOS/Linux
- **文字制限**: 32,000トークン（自動分割対応）
- **依存関係**: google-genai (v1.0+), python-dotenv
- **処理方式**: 非同期処理対応

### 利用可能なモデル

- `gemini-2.5-pro-preview-tts`: 最高品質（デフォルト）
- `gemini-2.5-flash-preview-tts`: コスト効率重視

## トラブルシューティング

### API キーエラー
```
Error: GEMINI_API_KEY environment variable is required
```
→ 環境変数 `GEMINI_API_KEY` を設定してください

### ファイルが見つからない
```
Error: Input file not found: filename.txt
```
→ 入力ファイルのパスを確認してください

## ライセンス

MIT License
