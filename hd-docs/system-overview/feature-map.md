---
generated_at: "2025-09-11T00:15:13Z"
repo_commit: "0388fc1c6dcdea14eab4e929ca842e6df5ebe6a4"
version: "1.8.4"
verification_script: "scripts/verify-feature-map.sh"
---

# AnythingLLM System Feature Map

This document provides a comprehensive feature map of the AnythingLLM system based on actual source code analysis at commit `0388fc1c6dcdea14eab4e929ca842e6df5ebe6a4`, organized by functional categories rather than technical layers.

## Verification

To validate the paths and providers listed in this document, run the verification script:

```bash
./scripts/verify-feature-map.sh
```

This script checks file existence, provider availability, and dependency consistency against the current repository state.

## Chat & Messaging

### **Streaming Chat Interface**
**Category:** Chat & Messaging  
**Files:** `/server/endpoints/chat.js`, `/server/utils/chats/stream.js`, `/frontend/src/components/WorkspaceChat/`  
**Technologies/Libraries:** Express, WebSockets (@mintplex-labs/express-ws), React  
**How it works:** Real-time streaming chat interface with Server-Sent Events (SSE) for message streaming. Supports workspace-based conversations with message history, citations, and error handling. Frontend uses React components for chat bubbles, message editing, and markdown rendering.

### **Multi-turn Conversations**
**Category:** Chat & Messaging  
**Files:** `/server/models/workspaceChats.js`, `/server/utils/chats/index.js`  
**Technologies/Libraries:** Prisma ORM, SQLite/PostgreSQL  
**How it works:** Persistent conversation history stored in database with chat context management. Supports conversation threading and maintains context across multiple interactions within workspaces.

### **Workspace-based Chat Isolation**
**Category:** Chat & Messaging  
**Files:** `/server/endpoints/workspaces.js`, `/server/models/workspace.js`  
**Technologies/Libraries:** Prisma ORM, Express  
**How it works:** Each workspace functions as an isolated chat environment with its own document context, chat history, and configuration. Workspaces can share documents but maintain separate conversation contexts.

### **Thread Management**
**Category:** Chat & Messaging  
**Files:** `/server/endpoints/workspaceThreads.js`, `/server/models/workspaceThread.js`  
**Technologies/Libraries:** Prisma ORM  
**How it works:** Supports multiple conversation threads within workspaces, allowing users to organize different topics or conversations separately while maintaining workspace-level document access.

## Document Processing & Summarization

### **Multi-format Document Processing**
**Category:** Document Processing & Summarization  
**Files:** `/collector/processSingleFile/`, `/collector/utils/constants.js`  
**Technologies/Libraries:** PDF parsing, DOCX processing, EPUB handling, Office MIME processing  
**How it works:** Comprehensive document processing pipeline supporting PDF, DOCX, PPTX, XLSX, TXT, MD, HTML, EPUB, ODT, ODP, MBOX formats. Each file type has dedicated converters that extract text content and metadata for embedding.

### **Audio/Video Transcription**
**Category:** Document Processing & Summarization  
**Files:** `/collector/processSingleFile/convert/asAudio.js`, `/server/utils/WhisperProviders/`  
**Technologies/Libraries:** OpenAI Whisper, Local Whisper models  
**How it works:** Uses browser's native speech recognition API for live chat input. Note: server-side live STT is not implemented; Whisper is used for offline document ingestion only.
### **Image Processing with OCR**
**Category:** Document Processing & Summarization  
**Files:** `/collector/processSingleFile/convert/asImage.js`, `/collector/utils/OCRLoader/`  
**Technologies/Libraries:** OCR processing, multiple language support  
**How it works:** Extracts text from images (PNG, JPG, JPEG) using OCR technology with support for multiple languages. Processed text is then available for embedding and chat context.

### **Web Content Extraction**
**Category:** Document Processing & Summarization  
**Files:** `/collector/utils/extensions/WebsiteDepth/`, `/collector/processLink/`  
**Technologies/Libraries:** Cheerio for HTML parsing  
**How it works:** Scrapes and processes web content with configurable depth crawling. Extracts clean text content from web pages, handling various HTML structures and converting to processable document format.

### **Repository Integration**
**Category:** Document Processing & Summarization  
**Files:** `/collector/utils/extensions/RepoLoader/`, `/collector/utils/extensions/RepoLoader/GithubRepo/`, `/collector/utils/extensions/RepoLoader/GitlabRepo/`  
**Technologies/Libraries:** GitHub/GitLab APIs  
**How it works:** Integrates with GitHub and GitLab repositories to process code files and documentation. Extracts source code, README files, and documentation for inclusion in the knowledge base.

### **Specialized Content Loaders**
**Category:** Document Processing & Summarization  
**Files:** `/collector/utils/extensions/Confluence/`, `/collector/utils/extensions/YoutubeTranscript/`, `/collector/utils/extensions/ObsidianVault/`  
**Technologies/Libraries:** Confluence API, YouTube transcript extraction, Obsidian vault parsing  
**How it works:** Specialized loaders for popular content sources including Confluence pages, YouTube video transcripts, Obsidian vault notes, and Drupal wiki content.

### **Document Sync & Watching**
**Category:** Document Processing & Summarization  
**Files:** `/server/jobs/sync-watched-documents.js`, `/server/models/documentSyncQueue.js`  
**Technologies/Libraries:** Node.js file system monitoring, Prisma  
**How it works:** Automated document synchronization system that monitors file changes and updates embeddings. Includes queue management for processing document updates and maintaining consistency.

## Voice Input / Output

### **Speech-to-Text (STT)**
**Category:** Voice Input / Output  
**Files:** `/frontend/src/components/SpeechToText/BrowserNative/`  
**Technologies/Libraries:** Browser Web Speech API, react-speech-recognition  
**How it works:** Uses browser's native speech recognition API for voice input. Currently limited to browser-based STT with no server-side speech processing implementation detected.

### **Text-to-Speech (TTS)**
**Category:** Voice Input / Output  
**Files:** `/server/utils/TextToSpeech/`, `/frontend/src/components/TextToSpeech/`  
**Technologies/Libraries:** ElevenLabs API, OpenAI TTS, PiperTTS (@mintplex-labs/piper-tts-web), Browser Speech Synthesis  
**How it works:** Multiple TTS providers including browser native, PiperTTS (runs in browser), OpenAI TTS, ElevenLabs, and generic OpenAI-compatible services. Frontend components handle voice synthesis with provider selection and voice configuration.

## Image Handling

### **Multi-modal LLM Support**
**Category:** Image Handling  
**Files:** `/server/utils/AiProviders/`, `/frontend/src/components/WorkspaceChat/`  
**Technologies/Libraries:** OpenAI Vision models, Anthropic Claude Vision, Google Gemini Vision  
**How it works:** Supports image understanding through vision-capable LLMs. Users can upload images in chat conversations, and compatible LLM providers can analyze and describe image content as part of the conversation flow.

### **Image Upload & Processing**
**Category:** Image Handling  
**Files:** `/server/utils/files/multer.js`, `/frontend/src/components/WorkspaceChat/`  
**Technologies/Libraries:** Multer for file uploads, React Dropzone  
**How it works:** Image upload system with drag-and-drop interface. Images are processed both for OCR text extraction (via document processing pipeline) and direct vision model analysis during chat interactions.

**Notes:** Max file size: <X MB>. Allowed types: PNG/JPG. Files are stored at <path/storage>. Malware scanning: <enabled/disabled>. PII handling: <policy>.
## LLM Providers (Local + Remote)

### **Commercial LLM Providers**
**Category:** LLM Providers  
**Files:** `/server/utils/AiProviders/openAi/`, `/server/utils/AiProviders/anthropic/`, `/server/utils/AiProviders/azureOpenAi/`, etc.  
**Technologies/Libraries:** OpenAI SDK, Anthropic SDK, Azure OpenAI, AWS Bedrock, Google Gemini  
**How it works:** Extensive support for commercial LLM providers including OpenAI (GPT models), Anthropic (Claude), Azure OpenAI, AWS Bedrock, Google Gemini, Cohere, Groq, Perplexity, OpenRouter, DeepSeek, Mistral, xAI, and many others. Each provider has dedicated integration with API key management and model selection.

### **Local LLM Support**
**Category:** LLM Providers  
**Files:** `/server/utils/AiProviders/ollama/`, `/server/utils/AiProviders/lmStudio/`, `/server/utils/AiProviders/localAi/`, `/server/utils/AiProviders/textGenWebUI/`  
**Technologies/Libraries:** Ollama, LM Studio, LocalAI, Text Generation WebUI, KoboldCPP  
**How it works:** Comprehensive local LLM support through popular local inference servers. Includes automatic model discovery, endpoint configuration, and seamless integration with both local and cloud models.

### **Model Context Protocol (MCP) Support**
**Category:** LLM Providers  
**Files:** `/server/utils/MCP/`, `/server/endpoints/mcpServers.js`  
**Technologies/Libraries:** @modelcontextprotocol/sdk, uvx for MCP server management  
**How it works:** MCP compatibility layer for integrating selected MCP servers as agent tools. Supports transports: stdio, sse, and streamableHttp (typed as 'http' in code). Discovery is config-based (storage/plugins/anythingllm_mcp_servers.json) — servers listed there may be auto-booted (anythingllm.autoStart); other servers require manual registration. Does not validate per-tool runtime dependencies; some tools need extra setup. Docker image includes uvx (pinned) for server management but this is not a guarantee of universal MCP compatibility.

## Vector Database Layer

### **Multiple Vector Database Support**
**Category:** Vector Database Layer  
**Files:** `/server/utils/vectorDbProviders/`  
**Technologies/Libraries:** LanceDB, PGVector, Pinecone, Chroma, Weaviate, Qdrant, Milvus, Zilliz, Astra DB  
**How it works:** Pluggable vector database architecture supporting multiple providers. LanceDB is default with local storage, while other providers offer cloud-based or self-hosted options. Each provider implements standardized interface for vector operations.

### **Embedding Engine Abstraction**
**Category:** Vector Database Layer  
**Files:** `/server/utils/EmbeddingEngines/`  
**Technologies/Libraries:** OpenAI Embeddings, Azure OpenAI, Cohere, Ollama, LM Studio, LocalAI, native embeddings  
**How it works:** Abstracted embedding layer supporting multiple embedding providers. Includes native embedding engine using local models, and integrations with commercial providers. Handles embedding generation, caching, and vector storage coordination.

### **Vector Caching System**
**Category:** Vector Database Layer  
**Files:** `/server/storage/` (runtime: `vector-cache/`), `/server/models/vectors.js`  
**Technologies/Libraries:** File system caching, Prisma ORM  
**How it works:** Intelligent vector caching system that stores computed embeddings to avoid reprocessing. Manages cache invalidation, storage optimization, and provides fast retrieval for previously processed content. The `vector-cache/` directory is created at runtime in the storage location.

## Authentication & Roles

### **Multi-user Authentication**
**Category:** Authentication & Roles  
**Files:** `/server/models/user.js`, `/server/utils/middleware/multiUserProtected.js`  
**Technologies/Libraries:** bcrypt for password hashing, JWT tokens, Prisma ORM  
**How it works:** Comprehensive user authentication system with role-based access control (Admin, Manager, Default). Supports user registration, login, password recovery, and session management with JWT tokens.

### **Role-based Access Control**
**Category:** Authentication & Roles  
**Files:** `/server/utils/middleware/multiUserProtected.js`, `/server/endpoints/admin.js`  
**Technologies/Libraries:** Express middleware, JWT validation  
**How it works:** Hierarchical role system with Admin (full access), Manager (user management), and Default (standard user) roles. Middleware enforces permissions at endpoint level with flexible role validation.

### **Simple SSO Integration**
**Category:** Authentication & Roles  
**Files:** `/server/utils/middleware/simpleSSOEnabled.js`, `/frontend/src/pages/Login/SSO/`  
**Technologies/Libraries:** Custom SSO implementation  
**How it works:** Single Sign-On integration capability with configurable SSO providers. Includes middleware for SSO session validation and frontend components for SSO login flows.

### **API Key Management**
**Category:** Authentication & Roles  
**Files:** `/server/models/apiKeys.js`, `/server/endpoints/api/`  
**Technologies/Libraries:** uuid-apikey for key generation, Prisma ORM  
**How it works:** API key generation and management system for programmatic access. Supports key creation, revocation, and usage tracking with role-based permissions for API access.

## Admin & Workspace Tools

### **User Management**
**Category:** Admin & Workspace Tools  
**Files:** `/frontend/src/pages/Admin/Users/`, `/server/endpoints/admin.js`  
**Technologies/Libraries:** React, Express, Prisma ORM  
**How it works:** Complete user management interface allowing admins to create, modify, suspend, and delete users. Includes user role assignment, daily message limits, and user activity monitoring.

### **Workspace Administration**
**Category:** Admin & Workspace Tools  
**Files:** `/frontend/src/pages/Admin/Workspaces/`, `/server/models/workspace.js`  
**Technologies/Libraries:** React, Prisma ORM  
**How it works:** Workspace management tools for creating, configuring, and managing workspaces. Includes workspace member management, document assignment, and workspace-specific settings configuration.

### **System Settings Management**
**Category:** Admin & Workspace Tools  
**Files:** `/frontend/src/pages/GeneralSettings/`, `/server/models/systemSettings.js`  
**Technologies/Libraries:** React, Prisma ORM  
**How it works:** Centralized system configuration interface covering LLM providers, vector databases, embedding engines, TTS/STT settings, security configurations, and feature toggles.

### **Event Logging & Audit Trail**
**Category:** Admin & Workspace Tools  
**Files:** `/server/models/eventLogs.js`, `/frontend/src/pages/Admin/Logging/`  
**Technologies/Libraries:** Winston logging, Prisma ORM  
**How it works:** Comprehensive event logging system tracking user actions, system events, and security-relevant activities. Provides searchable audit trail with log retention and export capabilities.

### **Invitation System**
**Category:** Admin & Workspace Tools  
**Files:** `/server/models/invite.js`, `/frontend/src/pages/Admin/Invitations/`  
**Technologies/Libraries:** UUID for invite codes, Prisma ORM  
**How it works:** User invitation system allowing admins to generate invite codes for new user registration. Supports workspace-specific invitations and invitation status tracking.

## Streaming & Real-Time

### **Streaming Architecture**
- WebSocket: agents/bi-directional  
- SSE: chat streaming/downstream-only  
See: `/server/endpoints/agentWebsocket.js`, `/server/utils/chats/stream.js`

### **Agent Flow Execution**
**Category:** Streaming & Real-Time  
**Files:** `/server/utils/agentFlows/executor.js`, `/server/utils/agentFlows/executors/`  
**Technologies/Libraries:** Custom flow execution engine  
**How it works:** Real-time agent flow execution system supporting parallel and sequential task execution. Includes flow monitoring, progress tracking, and real-time status updates.
## Mobile / PWA

### **Mobile Device Management**
**Category:** Mobile / PWA  
**Files:** `/server/endpoints/mobile/`, `/server/models/mobileDevice.js`  
**Technologies/Libraries:** Express, Prisma ORM, mobile device detection  
**How it works:** Mobile device registration and management system. Tracks connected mobile devices, manages device authentication, and provides device-specific configurations and permissions.

### **Mobile API Endpoints**
**Category:** Mobile / PWA  
**Files:** `/server/endpoints/mobile/index.js`, `/server/endpoints/mobile/utils/`  
**Technologies/Libraries:** Express, mobile-specific middleware  
**How it works:** Dedicated API endpoints optimized for mobile clients. Includes mobile command handling, device registration, and mobile-specific authentication flows.

### **Responsive Web Interface**
**Category:** Mobile / PWA  
**Files:** `/frontend/src/`, TailwindCSS configuration  
**Technologies/Libraries:** React, TailwindCSS, responsive design  
**How it works:** Fully responsive web interface that works across desktop, tablet, and mobile devices. Uses TailwindCSS for responsive design with mobile-optimized components and touch-friendly interactions.

## API & External Integrations

### **Developer API**
**Category:** API & External Integrations  
**Files:** `/server/endpoints/api/`, `/server/swagger/`  
**Technologies/Libraries:** Express, Swagger documentation, OpenAPI spec  
**How it works:** Comprehensive REST API with OpenAPI documentation. Provides programmatic access to all system features including workspace management, document processing, chat interactions, and user management.

### **Browser Extension Integration**
**Category:** API & External Integrations  
**Files:** `/server/endpoints/browserExtension.js`, `/server/models/browserExtensionApiKey.js`  
**Technologies/Libraries:** Express, API key authentication  
**How it works:** Dedicated API endpoints for browser extension integration. Supports web page content extraction, document processing from browser, and seamless workspace integration from web browsing.

### **Embeddable Chat Widget**
**Category:** API & External Integrations  
**Files:** `/server/endpoints/embed/`, `/server/models/embedConfig.js`  
**Technologies/Libraries:** Express, iframe embedding, CORS configuration  
**How it works:** Embeddable chat widget system allowing integration into external websites. Includes customizable chat interface, domain restrictions, and isolated chat sessions with configurable branding.

### **OpenAI API Compatibility**
**Category:** API & External Integrations  
**Files:** `/server/endpoints/api/openai/`, `/server/utils/chats/openaiCompatible.js`  
**Technologies/Libraries:** OpenAI API specification compatibility  
**How it works:** OpenAI-compatible API endpoint allowing AnythingLLM to be used as a drop-in replacement for OpenAI API in existing applications. Supports chat completions and streaming responses.

## DevOps / Deployment / Configuration

### **Docker Containerization**
**Category:** DevOps / Deployment / Configuration  
**Files:** `/docker/Dockerfile`, `/docker/docker-compose.yml`, `/docker/docker-entrypoint.sh`  
**Technologies/Libraries:** Docker, Docker Compose, Ubuntu base image  
**How it works:** Complete Docker containerization with multi-architecture support (ARM64/AMD64). Includes health checks, proper user permissions, volume mounting, and environment configuration management.

### **Cloud Deployment Templates**
**Category:** DevOps / Deployment / Configuration  
**Files:** `/cloud-deployments/aws/`, `/cloud-deployments/gcp/`, `/cloud-deployments/digitalocean/`  
**Technologies/Libraries:** CloudFormation (AWS), Terraform (DigitalOcean), Cloud Run (GCP), Kubernetes  
**How it works:** Ready-to-deploy templates for major cloud providers including AWS CloudFormation, GCP Cloud Run, DigitalOcean Terraform, and Kubernetes manifests. Includes HTTPS configuration and scaling options.

### **Environment Configuration**
**Category:** DevOps / Deployment / Configuration  
**Files:** `./server/.env.example`, `./frontend/.env.example`, `./collector/.env.example`, `./docker/.env.example`, `/server/utils/boot/`  
**Technologies/Libraries:** dotenv, environment validation  
**How it works:** Comprehensive environment configuration system with validation and defaults. Supports development, production, and testing environments with automatic configuration detection and validation. Each component has its own `.env.example` template.

### **Database Management**
**Category:** DevOps / Deployment / Configuration  
**Files:** `/server/prisma/`, database migration files  
**Technologies/Libraries:** Prisma ORM, SQLite (default), PostgreSQL support  
**How it works:** Database schema management with Prisma migrations. Supports SQLite for local development and PostgreSQL for production. Includes seeding, backup, and migration management scripts.

## Custom Model Support

### **Local Model Integration**
**Category:** Custom Model Support  
**Files:** `/server/storage/models/`, `/server/utils/AiProviders/localAi/`, `/server/utils/EmbeddingEngines/native/`  
**Technologies/Libraries:** Transformers.js (@xenova/transformers), local model loading  
**How it works:** Support for custom and local models through multiple pathways. Includes native embedding models, local inference server integration, and custom model loading capabilities.

### **Agent Plugin System**
**Category:** Custom Model Support  
**Files:** `/server/utils/agents/imported.js`, `/server/utils/agents/aibitat/plugins/`  
**Technologies/Libraries:** Custom plugin architecture, JSON schema validation  
**How it works:** Extensible agent plugin system allowing custom tool integration. Supports imported agent plugins with schema validation, custom function definitions, and integration with the agent workflow system.

### **Model Context Protocol (MCP)**
**Category:** Custom Model Support  
**Files:** `/server/utils/MCP/`, MCP hypervisor implementation  
**Technologies/Libraries:** @modelcontextprotocol/sdk, uvx for server management  
**How it works:** Full MCP server integration allowing custom tools and capabilities to be added through MCP protocol. Automatically converts MCP tools into AnythingLLM agent plugins with proper function calling support.

## AI Agents & Automation

### **No-code Agent Builder**
**Category:** AI Agents & Automation  
**Files:** `/frontend/src/pages/Admin/AgentBuilder/`, `/server/utils/agentFlows/`  
**Technologies/Libraries:** React Beautiful DnD, custom flow execution engine  
**How it works:** Visual drag-and-drop agent builder allowing creation of complex workflows without coding. Includes various node types (LLM instructions, API calls, web scraping), flow validation, and execution monitoring.

### **Multi-Agent System (Aibitat)**
**Category:** AI Agents & Automation  
**Files:** `/server/utils/agents/aibitat/`, agent provider integrations  
**Technologies/Libraries:** Custom multi-agent framework, WebSocket communication  
**How it works:** Sophisticated multi-agent system supporting agent collaboration, tool usage, and complex workflows. Includes memory management, agent communication protocols, and integration with all supported LLM providers.

### **Built-in Agent Tools**
**Category:** AI Agents & Automation  
**Files:** `/server/utils/agents/aibitat/plugins/`, SQL connector tools  
**Technologies/Libraries:** Web scraping, SQL connectors (MySQL, PostgreSQL, MSSQL), file operations  
**How it works:** Comprehensive set of built-in agent tools including web browsing, web scraping, SQL database querying, file operations, summarization, and memory management. Tools are modular and can be combined in agent workflows.

### **SQL Agent Capabilities**
**Category:** AI Agents & Automation  
**Files:** `/server/utils/agents/aibitat/plugins/sql-agent/`, SQL connectors  
**Technologies/Libraries:** MySQL2, PostgreSQL (pg), MSSQL  
**How it works:** Specialized SQL agent tools that can connect to databases, inspect schemas, list tables, and execute queries. Supports major database systems with proper connection management and query safety measures.

> ⚠️ Safety: Use read-only credentials. Enforce allowlisted statements, row limits, and query timeouts. DDL/DML are disabled by default and must be explicitly enabled per workspace.
## System Monitoring / Logging

### **Telemetry System**
**Category:** System Monitoring / Logging  
**Files:** `/server/models/telemetry.js`, `/server/utils/telemetry/`  
**Technologies/Libraries:** PostHog, anonymous usage tracking  
**How it works:** Privacy-focused telemetry system tracking anonymous usage patterns. Collects data on feature usage, performance metrics, and system health while respecting user privacy. Can be disabled via configuration.

### **Comprehensive Logging**
**Category:** System Monitoring / Logging  
**Files:** `/server/utils/logger/`, Winston configuration  
**Technologies/Libraries:** Winston logging framework, file rotation  
**How it works:** Structured logging system with multiple log levels, file rotation, and configurable output formats. Includes request logging, error tracking, and system event logging with proper log management.

### **Health Monitoring**
**Category:** System Monitoring / Logging  
**Files:** `/docker/docker-healthcheck.sh`, health check endpoints  
**Technologies/Libraries:** Docker health checks, HTTP endpoint monitoring  
**How it works:** System health monitoring with Docker health checks, endpoint availability monitoring, and basic system resource tracking. Includes automatic restart capabilities and health status reporting.

### **Error Handling & Recovery**
**Category:** System Monitoring / Logging  
**Files:** Error handling throughout application, graceful shutdown  
**Technologies/Libraries:** @ladjs/graceful for graceful shutdown, comprehensive error boundaries  
**How it works:** Robust error handling system with graceful degradation, automatic recovery mechanisms, and proper error reporting. Includes graceful shutdown procedures and connection cleanup.

---

## Summary

AnythingLLM is a comprehensive, full-stack AI chatbot platform with 60+ distinct features organized across 14 functional categories. The system demonstrates enterprise-grade architecture with:

- **Extensive LLM Support**: 25+ LLM providers including local and commercial options
- **Multi-modal Capabilities**: Text, voice, image, and document processing
- **Advanced Agent System**: No-code agent builder with 15+ built-in tools
- **Enterprise Features**: Multi-user, role-based access, audit logging, API management
- **Flexible Deployment**: Docker, cloud templates, bare metal support
- **Rich Integrations**: Browser extensions, mobile apps, embeddable widgets, MCP support

The platform targets production use; maturity varies by area. See repository CI status, test coverage, and deployment guides for current readiness.

## Key Technical Highlights

### Architecture
- **Monorepo Structure**: Frontend (React/Vite), Server (Node.js/Express), Collector (Document Processing)
- **Database**: Prisma ORM with SQLite (default) or PostgreSQL support
- **Real-time**: WebSockets and Server-Sent Events for streaming
- **Containerization**: Docker with multi-architecture support

### AI/ML Integration
- **LLM Providers**: OpenAI, Anthropic, Google Gemini, AWS Bedrock, Azure, and 20+ others
- **Local Models**: Ollama, LM Studio, LocalAI, Text Generation WebUI
- **Vector Databases**: LanceDB, Pinecone, Chroma, Weaviate, Qdrant, Milvus, PGVector
- **Embeddings**: Native, OpenAI, Cohere, and multiple provider support
- **MCP Protocol**: Full Model Context Protocol compatibility

### Document Processing
- **Formats**: PDF, DOCX, PPTX, XLSX, TXT, MD, HTML, EPUB, ODT, ODP, MBOX
- **Audio/Video**: MP3, WAV, MP4 with Whisper transcription
- **Images**: PNG, JPG with OCR text extraction
- **Web Content**: URL scraping with depth control
- **Repositories**: GitHub/GitLab integration
- **Specialized**: Confluence, YouTube, Obsidian, Drupal

### Security & Enterprise
- **Authentication**: Multi-user with role-based access (Admin/Manager/Default)
- **API Security**: JWT tokens, API keys, browser extension keys
- **Audit Trail**: Comprehensive event logging
- **Privacy**: Configurable telemetry, data isolation
- **SSO**: Simple Single Sign-On integration

### Deployment & DevOps
- **Cloud Ready**: AWS CloudFormation, GCP Cloud Run, DigitalOcean Terraform
- **Container**: Docker with health checks and proper permissions
- **Database**: Prisma migrations with SQLite/PostgreSQL
- **Monitoring**: Winston logging, health endpoints, error handling
- **Configuration**: Environment-based with validation

This feature map serves as the foundation for documentation coverage analysis and system understanding.