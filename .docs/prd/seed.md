### Gemini Pro TTS CLI ― MVP要件定義

#### 1. 目的

* ローカル環境の CLI から **Gemini 2.5 Pro Preview TTS** を呼び出し、テキストファイルを **WAV（PCM 16-bit, 24 kHz）** に変換する。
* **スタイル指示（Style instructions）** と **音声（voice）** をオプションで切り替え可能。既定は

  * **Style**: `reads aloud in a high school girl, vivacious, fresh, lively, fast-talking and smooth, Japanese anime-style voice:`
  * **Voice**: `Zephyr`（公式 30 voice の 1 つ）([ai.google.dev][1])

#### 2. 入出力仕様

| パラメータ          | 必須 | 型    | 既定値                          | 説明                                   |
| -------------- | -- | ---- | ---------------------------- | ------------------------------------ |
| `--input, -i`  | ○  | path | ―                            | 読み込む UTF-8 テキストファイル                  |
| `--output, -o` | ○  | path | ―                            | 書き出す WAV ファイル                        |
| `--style, -s`  | ―  | str  | 上記既定                         | 先頭に付加するスタイル指示文                       |
| `--voice, -v`  | ―  | str  | Zephyr                       | Gemini TTS の `voice_name`（30 種類から選択） |
| `--model`      | ―  | str  | `gemini-2.5-pro-preview-tts` | 利用 TTS モデル名([ai.google.dev][1])      |

#### 3. 機能要件

1. **テキスト読込**

   * UTF-8 で全行を取得。
   * 32 k token 制限を超える場合は自動で段落単位に分割し、順次 API 呼び出しし、音声バッファを結合する。([ai.google.dev][1])

2. **Gemini API 呼び出し**

   * `google-generativeai` ライブラリを使用。
   * `response_modalities=["AUDIO"]` とし、`speech_config.voice_config.prebuilt_voice_config.voice_name` に `--voice` を設定。
   * スタイル指示は **入力テキストの先頭にプレフィックス**として付加（TTS は自然言語でのスタイル制御を推奨）。([ai.google.dev][1])

3. **WAV 生成**

   * 受信したバイナリストリームを `wave` モジュールで 16-bit PCM/24 kHz/mono に保存。
   * 分割生成した場合も 1 本の WAV に連結して書き出す。

4. **CLI 挙動**

   * 必須引数が不足した場合は `--help` を表示し終了。
   * 進捗を標準出力に簡易表示（例: `Chunk 1/3 … done`).
   * エラー時は非 0 終了コード。

#### 4. 非機能要件

* **環境**: Python 3.9+、macOS/Linux 対応。
* **依存**: `google-generativeai>=0.5.*` 以外は標準ライブラリのみ。
* **設定**: 環境変数 `GEMINI_API_KEY` に API キーを格納。
* **ログ**: `--verbose` でデバッグログを表示。

#### 5. 拡張余地（MVP 外）

* MP3／OGG 出力切替
* マルチスピーカースクリプト（speaker: line 形式）対応
* GUI ラッパー、Docker イメージ

---

> **実装イメージ（参考）**
>
> ```bash
> python gemini_tts_cli.py \
>   --input script.txt \
>   --output result.wav \
>   --style "whispering, mysterious tone:" \
>   --voice Kore
> ```

これが MVP 実装の最終要件定義です。

[1]: https://ai.google.dev/gemini-api/docs/speech-generation "Speech generation (text-to-speech)  |  Gemini API  |  Google AI for Developers"
