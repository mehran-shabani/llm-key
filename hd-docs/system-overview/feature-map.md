# Feature Map — AnythingLLM System

This document provides a feature-oriented breakdown of the AnythingLLM codebase, mapping core functionalities to their respective implementations, technologies, and files. It is meant to guide contributors and reviewers in understanding **how each feature works**, based on source code — not assumptions.

---

## 📡 1. Chat Interface & Real-Time Messaging

- **Files**: 
  - `frontend/src/pages/Chat.tsx`
  - `server/ws/`, `server/sse/`
- **Libraries**:
  - React, WebSocket, Server-Sent Events (SSE)
- **How it works**:
  - Frontend sends user input via REST or WebSocket
  - Server streams LLM responses using SSE
  - Maintains chat state with local session cache

---

## 📄 2. Document Summarization & Processing

- **Files**:
  - `collector/`, `server/controllers/documents.ts`
- **Libraries**:
  - pdf-parse, mammoth, Tesseract.js, Puppeteer
- **How it works**:
  - Documents uploaded via frontend or API
  - `collector/` handles format detection, OCR, text extraction
  - Extracted content is embedded and stored in vector DB

---

## 🧠 3. LLM Integration (Cloud & Local)

- **Files**:
  - `server/llm/`, `server/providers/`
- **Libraries**:
  - OpenAI SDK, LocalAI, Anthropic, Ollama, etc.
- **How it works**:
  - Strategy pattern selects the appropriate LLM provider
  - Input is routed to the provider, response streamed back

---

## 🖼 4. Image Upload & Interpretation

- **Files**:
  - `collector/image-handler.ts`, `server/controllers/image.ts`
- **Libraries**:
  - Sharp, Tesseract.js
- **How it works**:
  - User uploads image → Collector extracts text or features
  - May be routed to LLM with system prompt for interpretation

---

## 🎤 5. Voice Input & TTS/STT

- **Files**:
  - `frontend/audio/`, `server/audio/`
- **Libraries**:
  - Web Audio API, Whisper, Coqui TTS
- **How it works**:
  - Audio recorded in browser → sent to server → transcribed
  - TTS responses optionally streamed back to client

---

## 🔐 6. Authentication & User Management

- **Files**:
  - `server/auth/`, `server/routes/user.ts`
- **Libraries**:
  - bcrypt, JWT, Express middleware
- **How it works**:
  - Multi-mode authentication (token-based or password)
  - Role-based access enforced at route and component level

---

## 🔍 7. Vector Database Layer

- **Files**:
  - `server/vector/`, `server/db/index.ts`
- **Libraries**:
  - LanceDB, Pinecone, Chroma, Qdrant
- **How it works**:
  - Text chunks embedded and stored in selected vector DB
  - Search performed via cosine similarity or custom strategy

---

## 🧩 8. Custom Model Support

- **Files**:
  - `server/providers/custom.ts`
- **Libraries**:
  - Custom runtime interface (CLI, REST, local process)
- **How it works**:
  - Interface wraps external models as compatible providers
  - Models executed via subprocess or API calls

---

## 📱 9. Mobile Support / PWA

- **Files**:
  - `frontend/pwa.ts`, `manifest.json`
- **Libraries**:
  - PWA APIs, Tailwind responsive config
- **How it works**:
  - App installable on mobile devices with offline caching
  - Responsive layouts + touch input compatibility

---

## 🛠 10. System Operations & DevOps

- **Files**:
  - `Dockerfile`, `docker-compose.yml`, `k8s/`
- **Technologies**:
  - Docker, Kubernetes, PM2, nginx
- **How it works**:
  - Multi-service deployment via Docker Compose
  - Production orchestration with Kubernetes or single binary

---

## 🔁 11. Streaming Infrastructure

- **Files**:
  - `server/sse/`, `server/ws/`, `frontend/hooks/useStream.ts`
- **Libraries**:
  - EventSource API, WebSocket, SSE fallback
- **How it works**:
  - Server streams LLM output as it's generated
  - Client renders tokens incrementally in chat window

---

> This feature map is automatically or manually updated during major system changes and serves as the baseline for documentation audits and onboarding.
