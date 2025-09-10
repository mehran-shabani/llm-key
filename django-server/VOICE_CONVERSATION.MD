# VOICE_CONVERSATION – Chain همگام (بدون استریم)

Pipeline:
1) STT (OpenAI Whisper: `stt` دسته) → transcript
2) LLM (دسته `text_gen` یا `text2text` طبق نیاز) → پاسخ متنی
3) TTS (OpenAI TTS: `tts` دسته) → خروجی صوت (base64 یا فایل)

قوانین:
- فقط OpenAI؛ مدل‌ها از `MODEL_LIST.md`.
- override مدل‌ها در درخواست مجاز اما اگر نامعتبر بود → fallback به default.
- کلاینت OpenAI باید هم `API Base URL` و هم `API Key` را از هدر **یا** env بگیرد.
- خروجی نهایی: `{ transcript, text_response, audio(base64|file), models_used }`
