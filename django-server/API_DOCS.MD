# API_DOCS

<!-- BEGIN: AUTH -->
<!-- END: AUTH -->

<!-- BEGIN: ADMIN -->
<!-- END: ADMIN -->

<!-- BEGIN: SYSTEM -->
<!-- END: SYSTEM -->

<!-- BEGIN: WORKSPACES -->
<!-- END: WORKSPACES -->

<!-- BEGIN: CHATS -->
<!-- END: CHATS -->

<!-- BEGIN: DOCUMENTS -->
<!-- END: DOCUMENTS -->

<!-- BEGIN: FILES -->
<!-- END: FILES -->

<!-- BEGIN: LLM -->
## LLM Endpoints

### POST /api/llm/generate/
Generate text using OpenAI chat completions (category: text_gen).

**Request Body:**
```json
{
  "model": "gpt-4o",  // Optional, defaults to text_gen default
  "messages": [
    {"role": "user", "content": "Hello, world!"}
  ],
  "temperature": 0.7,  // Optional, 0-2
  "max_tokens": 100,   // Optional
  "top_p": 1.0,        // Optional, 0-1
  "frequency_penalty": 0.0,  // Optional, -2 to 2
  "presence_penalty": 0.0,   // Optional, -2 to 2
  "stop": ["\n", "."]  // Optional, list of stop sequences
}
```

**Response:**
```json
{
  "content": "Generated text response",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key

### POST /api/llm/instruct/
Generate text using OpenAI chat completions for instruction following (category: text2text).

**Request Body:**
```json
{
  "model": "gpt-4o-mini",  // Optional, defaults to text2text default
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing"}
  ],
  "temperature": 0.7,  // Optional, 0-2
  "max_tokens": 500,   // Optional
  "top_p": 1.0,        // Optional, 0-1
  "frequency_penalty": 0.0,  // Optional, -2 to 2
  "presence_penalty": 0.0,   // Optional, -2 to 2
  "stop": ["\n\n"]     // Optional, list of stop sequences
}
```

**Response:**
```json
{
  "content": "Detailed explanation of quantum computing...",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 200,
    "total_tokens": 215
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
<!-- END: LLM -->

<!-- BEGIN: EMBEDDING -->
## Embedding Endpoints

### POST /api/embedding/
Generate embedding using OpenAI embeddings API (category: embedding).

**Request Body:**
```json
{
  "model": "text-embedding-3-small",  // Optional, defaults to embedding default
  "input": "Text to generate embedding for",
  "encoding_format": "float"  // Optional, defaults to "float"
}
```

**Response:**
```json
{
  "embedding": [0.1, -0.2, 0.3, ...],  // Array of float values
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
<!-- END: EMBEDDING -->

<!-- BEGIN: IMAGE -->
## Image Endpoints

### POST /api/image/generate/
Generate image using OpenAI images API (category: image).

**Request Body:**
```json
{
  "model": "gpt-image-1",  // Optional, defaults to image default
  "prompt": "A beautiful sunset over mountains",
  "n": 1,                  // Optional, number of images (1-10)
  "size": "1024x1024",     // Optional, image size
  "quality": "standard",  // Optional, "standard" or "hd"
  "style": "vivid",        // Optional, "vivid" or "natural"
  "user": "user123"        // Optional, user identifier
}
```

**Response:**
```json
{
  "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
  "revised_prompt": "A beautiful sunset over mountains with vibrant colors"
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
<!-- END: IMAGE -->

<!-- BEGIN: STT -->
<!-- END: STT -->

<!-- BEGIN: TTS -->
<!-- END: TTS -->

<!-- BEGIN: CONVERSATION -->
<!-- END: CONVERSATION -->

<!-- BEGIN: SCHEMA -->
<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
<!-- END: JOBS -->
