# AnythingLLM - System Architecture Overview

## Executive Summary

AnythingLLM is a comprehensive, full-stack application that transforms private documents into an intelligent chat interface using Large Language Models (LLMs) and vector databases. The system employs a **microservices-oriented monorepo architecture** with three core services: a main API server, a dedicated document processing service, and a modern React frontend.

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AnythingLLM System                      │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React SPA)           │  Backend Services             │
│  ├── User Interface             │  ├── Main Server (Port 3001)  │
│  ├── Real-time Chat             │  │   ├── REST API Endpoints   │
│  ├── Document Management        │  │   ├── WebSocket Server     │
│  ├── Admin Controls             │  │   ├── Authentication       │
│  └── Multi-language Support     │  │   └── Business Logic       │
│                                 │  └── Collector (Port 8888)   │
│                                 │      ├── Document Processing │
│                                 │      ├── Web Scraping        │
│                                 │      └── Format Conversion   │
├─────────────────────────────────────────────────────────────────┤
│                        Data Layer                              │
│  ├── SQLite/PostgreSQL (Prisma ORM)                           │
│  ├── Vector Databases (LanceDB, Pinecone, Chroma, etc.)       │
│  ├── File Storage (Documents, Models, Cache)                  │
│  └── Configuration Management                                 │
├─────────────────────────────────────────────────────────────────┤
│                    External Integrations                       │
│  ├── LLM Providers (OpenAI, Anthropic, Local Models)          │
│  ├── Embedding Services (Native, OpenAI, Cohere)              │
│  ├── Speech Services (TTS/STT)                                │
│  └── Search Providers (Google, Bing, etc.)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Core System Components

### 1. **Frontend Application** (`frontend/`)
- **Technology**: React 18 + Vite + Tailwind CSS
- **Architecture**: Single Page Application (SPA) with lazy loading
- **Port**: 3000 (development) / served from server in production
- **Key Features**:
  - Real-time chat interface with streaming responses
  - Multi-language support (20+ languages)
  - Role-based access control (Admin/Manager/User)
  - Dark/light theme system with CSS variables
  - Mobile-responsive design
  - Drag-and-drop file uploads

### 2. **Main Server** (`server/`)
- **Technology**: Node.js + Express + Prisma ORM
- **Architecture**: Layered MVC with middleware pipeline
- **Port**: 3001
- **Key Responsibilities**:
  - REST API endpoints for all application features
  - WebSocket server for real-time chat streaming
  - User authentication and session management
  - Workspace and document management
  - LLM and vector database orchestration
  - Background job processing

### 3. **Document Collector** (`collector/`)
- **Technology**: Node.js + Express + Puppeteer + OCR
- **Architecture**: Pipeline-based document processing
- **Port**: 8888
- **Key Responsibilities**:
  - File format conversion (PDF, DOCX, images, etc.)
  - Web scraping with headless Chrome
  - OCR processing for images and scanned documents
  - Text extraction and preprocessing
  - Document metadata generation

## Data Flow Architecture

### Document Processing Pipeline
```
User Upload → Collector Service → Format Detection → Converter → 
Text Extraction → Tokenization → Vector Embedding → Storage → 
Main Server → Vector Database
```

### Chat Interaction Flow
```
User Message → Frontend → Main Server → Context Retrieval → 
Vector Search → LLM Provider → Streaming Response → 
Frontend Display
```

### Real-Time Communication
```
Frontend ←→ Server-Sent Events ←→ Main Server ←→ WebSocket ←→ 
LLM Provider (streaming)
```

## Technology Stack Deep Dive

### Backend Technologies
- **Runtime**: Node.js 18+ with ES modules
- **Web Framework**: Express.js 5.x with middleware architecture
- **Database**: 
  - **Primary**: SQLite (default) with Prisma ORM
  - **Production**: PostgreSQL, MySQL support
  - **Vector**: LanceDB (default), 10+ vector database options
- **Authentication**: JWT tokens with bcrypt password hashing
- **Real-time**: WebSocket + Server-Sent Events
- **File Processing**: 
  - **PDF**: pdf-parse with OCR fallback (Tesseract.js)
  - **Office**: mammoth (DOCX), officeparser (PPTX, ODT)
  - **Web**: Puppeteer with headless Chrome
  - **Images**: Sharp + Tesseract.js OCR

### Frontend Technologies
- **Framework**: React 18 with hooks and context
- **Build Tool**: Vite with hot module replacement
- **Styling**: Tailwind CSS with custom theme system
- **Routing**: React Router v6 with lazy loading
- **State Management**: React Context + local state
- **Internationalization**: i18next with 20+ languages
- **Icons**: Phosphor Icons
- **UI Components**: Custom components + Tremor charts

### Infrastructure & Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose, Kubernetes
- **Cloud Platforms**: AWS, GCP, DigitalOcean one-click deployments
- **Process Management**: PM2, systemd support
- **Reverse Proxy**: nginx, Apache configurations included

## Integration Architecture

### LLM Provider Abstraction
The system implements a **strategy pattern** for LLM providers:

```javascript
const LLMProvider = getLLMProviderClass({ provider });
const response = await LLMProvider.chat(messages, workspace);
```

**Supported Providers** (25+):
- **Commercial**: OpenAI, Anthropic, Google Gemini, AWS Bedrock
- **Local**: Ollama, LMStudio, LocalAI, llama.cpp
- **Hosted**: Together AI, Fireworks, Perplexity, OpenRouter

### Vector Database Abstraction
Similar strategy pattern for vector databases:

```javascript
const VectorDB = getVectorDbClass();
await VectorDB.addDocumentChunks(chunks, workspace);
```

**Supported Databases** (10+):
- **Local**: LanceDB (default)
- **Cloud**: Pinecone, Weaviate, Qdrant
- **Self-hosted**: Chroma, Milvus, PGVector

### Authentication Modes
The system supports multiple authentication patterns:

1. **Single User Mode**: No authentication required
2. **Password Protected**: Single password for all users
3. **Multi-User Mode**: Individual user accounts with roles

## Scalability & Performance Architecture

### Microservice Benefits
- **Service Isolation**: Document processing failures don't affect chat
- **Resource Optimization**: CPU-intensive processing isolated
- **Independent Scaling**: Services can scale independently
- **Technology Flexibility**: Different services can use optimal tech stacks

### Performance Optimizations
- **Frontend**: Code splitting, lazy loading, bundle optimization
- **Backend**: Connection pooling, query optimization, caching
- **Document Processing**: Parallel processing, format-specific optimizations
- **Vector Operations**: Efficient similarity search with configurable thresholds

### Deployment Scalability
- **Single Container**: All services in one container for simplicity
- **Multi-Container**: Separate containers for horizontal scaling
- **Kubernetes**: Full orchestration with persistent volumes
- **Cloud Native**: Auto-scaling groups, load balancers, managed databases

## Security Architecture

### Multi-Layer Security
1. **Application Layer**:
   - JWT token authentication
   - Role-based access control (RBAC)
   - Input validation and sanitization
   - SQL injection prevention (Prisma ORM)

2. **Network Layer**:
   - CORS configuration
   - HTTPS support with automatic redirects
   - Request rate limiting
   - Payload integrity verification

3. **Container Layer**:
   - Non-root user execution
   - Minimal base images
   - Security scanning integration
   - Capability restrictions

### Data Privacy
- **Local Processing**: All data can remain on-premises
- **Configurable Telemetry**: Optional usage analytics
- **Encryption**: Sensitive data encryption at rest
- **Access Logging**: Comprehensive audit trails

## Notable Architectural Decisions

### 1. **Monorepo with Service Separation**
**Decision**: Single repository with multiple service directories
**Benefits**:
- Coordinated development and releases
- Shared tooling and configuration
- Simplified dependency management
- Unified documentation and testing

### 2. **Microservices in Single Container**
**Decision**: Deploy all services in one container by default
**Benefits**:
- Simplified deployment for end users
- Reduced networking complexity
- Easier resource management
- Single point of monitoring

### 3. **Provider Abstraction Pattern**
**Decision**: Abstract LLM and vector database providers
**Benefits**:
- Vendor independence
- Easy provider switching
- Consistent API across providers
- Future-proof architecture

### 4. **Real-Time Streaming Architecture**
**Decision**: Use Server-Sent Events for chat streaming
**Benefits**:
- Lower latency than polling
- Better user experience
- Efficient resource utilization
- Browser compatibility

### 5. **Multi-Architecture Docker Support**
**Decision**: Support both ARM64 and AMD64 architectures
**Benefits**:
- Apple Silicon compatibility
- ARM cloud instance support
- Cost optimization opportunities
- Broader deployment options

## System Capabilities Summary

### Core Features
- **Document Intelligence**: Transform any document into searchable, chatbot-accessible knowledge
- **Multi-Modal Support**: Text, images, audio, video processing
- **Real-Time Chat**: Streaming responses with context awareness
- **Multi-Tenancy**: Workspace isolation with user management
- **Extensibility**: Plugin architecture for custom integrations

### Enterprise Features
- **Role-Based Access**: Admin, Manager, User role hierarchy
- **Audit Logging**: Comprehensive activity tracking
- **API Access**: Full REST API for custom integrations
- **Embedding Widgets**: Embeddable chat for websites
- **Mobile Support**: Progressive web app capabilities

### Developer Features
- **Open Source**: MIT licensed with community contributions
- **Extensible**: Plugin system for custom providers
- **Well-Documented**: Comprehensive API documentation
- **Docker Ready**: Production-ready containerization
- **Cloud Native**: Kubernetes and cloud platform support

This architecture enables AnythingLLM to serve use cases ranging from personal document management to enterprise knowledge management systems, with the flexibility to deploy anywhere from a local laptop to a multi-region cloud deployment.