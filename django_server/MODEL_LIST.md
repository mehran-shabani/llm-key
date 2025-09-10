# MODEL_LIST – فقط OpenAI

> کد فقط باید اولین بلوک JSON را بخواند.

```json
{
  "text_gen": {
    "default": "gpt-4o",
    "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"]
  },
  "text2text": {
    "default": "gpt-4o-mini",
    "models": ["gpt-4o-mini", "gpt-4.1-mini"]
  },
  "image": {
    "default": "gpt-image-1",
    "models": ["gpt-image-1"]
  },
  "embedding": {
    "default": "text-embedding-3-small",
    "models": ["text-embedding-3-small", "text-embedding-3-large"]
  },
  "tts": {
    "default": "tts-1",
    "models": ["tts-1", "tts-1-hd"]
  },
  "stt": {
    "default": "whisper-1",
    "models": ["whisper-1"]
  }
}
```