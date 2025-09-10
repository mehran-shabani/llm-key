# AnythingLLM Server - Backend Architecture

## Purpose
The server component is the core backend service of AnythingLLM, providing REST APIs, WebSocket connections, and orchestrating interactions between LLMs, vector databases, and document processing services.

## Technologies Used
- **Express.js**: Web framework for REST API and middleware
- **Prisma**: Database ORM with SQLite/PostgreSQL support
- **WebSocket**: Real-time communication via `@mintplex-labs/express-ws`
- **bcrypt**: Password hashing and authentication
- **JWT**: Token-based authentication
- **Winston**: Structured logging
- **Multer**: File upload handling
- **CORS**: Cross-origin resource sharing

## Architecture Overview

### Core Server Structure
The server follows a **layered architecture** with clear separation of concerns:

```
server/
├── index.js           # Main application entry point
├── endpoints/         # REST API route handlers
├── models/           # Data access layer (Prisma models)
├── utils/            # Shared utilities and helpers
├── prisma/           # Database schema and migrations
├── middleware/       # Custom middleware functions
└── storage/          # File storage and vector cache
```

### Key Architectural Patterns

#### 1. **Model-View-Controller (MVC) Pattern**
- **Models**: Data access layer in `models/` directory
- **Controllers**: API endpoint handlers in `endpoints/`
- **Views**: JSON responses (no traditional views in this API)

#### 2. **Middleware Pipeline Architecture**
```javascript
// Example middleware chain
app.use(cors({ origin: true }));
app.use(bodyParser.json({ limit: FILE_LIMIT }));
app.use("/api", apiRouter);

// Route-specific middleware
app.post("/workspace/new", [
  validatedRequest,
  flexUserRoleValid([ROLES.admin, ROLES.manager])
], handlerFunction);
```

#### 3. **Plugin-Based Extension System**
The server supports extensible functionality through:
- **Endpoint modules**: Each feature area has its own endpoint file
- **Provider abstraction**: LLM and Vector DB providers are pluggable
- **Middleware composition**: Reusable middleware components

## Core Components

### 1. Application Bootstrap (`index.js`)
```javascript
// Dynamic environment loading
process.env.NODE_ENV === "development"
  ? require("dotenv").config({ path: `.env.${process.env.NODE_ENV}` })
  : require("dotenv").config();

// SSL/HTTP server initialization
if (!!process.env.ENABLE_HTTPS) {
  bootSSL(app, process.env.SERVER_PORT || 3001);
} else {
  bootHTTP(app, process.env.SERVER_PORT || 3001);
}
```

**Technical Decisions**:
- **Environment-specific configuration**: Supports development/production env files
- **Conditional HTTPS**: SSL support with fallback to HTTP
- **Large file handling**: 3GB file size limit for document processing
- **WebSocket integration**: Conditionally loaded based on HTTPS configuration

### 2. Database Layer (Prisma + Models)

#### Schema Design Patterns
```prisma
// Multi-tenant workspace isolation
model workspaces {
  id                  Int                 @id @default(autoincrement())
  slug                String              @unique
  workspace_users     workspace_users[]   // Many-to-many with users
  documents          workspace_documents[] // One-to-many with documents
  workspace_chats    workspace_chats[]    // One-to-many with chats
}

// Role-based access control
model users {
  id                 Int      @id @default(autoincrement())
  role              String   @default("default") // admin, manager, default
  workspace_users   workspace_users[]
}
```

#### Model Abstraction Layer
The `models/` directory implements a **repository pattern** with validation:

```javascript
// Example from workspace.js
const Workspace = {
  // Input validation
  validations: {
    name: (value) => String(value).slice(0, 255),
    openAiTemp: (value) => {
      const temp = parseFloat(value);
      if (isNullOrNaN(temp) || temp < 0) return null;
      return temp;
    }
  },

  // Create with validation
  new: async function (name, creatorId, additionalFields = {}) {
    const workspace = await prisma.workspaces.create({
      data: {
        name: this.validations.name(name),
        ...this.validateFields(additionalFields),
        slug: this.slugify(name, { lower: true })
      }
    });
    return { workspace, message: null };
  }
}
```

**Technical Decisions**:
- **Input validation at model layer**: Prevents invalid data at database level
- **Slugification for URLs**: Safe URL generation with collision handling
- **Soft relationships**: Some foreign keys omitted to prevent migration issues
- **Audit trail**: Event logging and telemetry tracking for changes

### 3. Authentication & Authorization

#### Multi-User Mode Support
```javascript
// From systemSettings.js
isMultiUserMode: async function () {
  const setting = await this.get({ label: "multi_user_mode" });
  return setting?.value === "true";
}

// Role-based middleware
const { ROLES } = require("../utils/middleware/multiUserProtected");
// ROLES: { admin: "admin", manager: "manager", default: "default" }
```

#### Security Implementation
- **Password complexity validation**: Configurable via environment variables
- **bcrypt hashing**: Industry-standard password hashing
- **JWT tokens**: Stateless authentication
- **Role-based access control**: Admin/Manager/Default user roles
- **Session management**: Temporary auth tokens for mobile apps

### 4. API Endpoint Architecture

#### Modular Endpoint Organization
```javascript
// From index.js - endpoint registration
systemEndpoints(apiRouter);
workspaceEndpoints(apiRouter);
chatEndpoints(apiRouter);
adminEndpoints(apiRouter);
// ... other endpoints
```

#### Request/Response Pattern
```javascript
// Example from workspaces.js
app.post("/workspace/new", [
  validatedRequest,                    // Input validation
  flexUserRoleValid([ROLES.admin, ROLES.manager])  // Authorization
], async (request, response) => {
  const { name, ...additionalFields } = reqBody(request);
  const user = await userFromSession(request, response);
  
  const { workspace, message } = await Workspace.new(
    name, 
    user?.id, 
    additionalFields
  );
  
  response.status(200).json({ workspace, message });
});
```

**Key Features**:
- **Middleware composition**: Validation and authorization as reusable middleware
- **Consistent error handling**: Standardized error responses
- **Request body parsing**: Centralized request body extraction
- **User session management**: Automatic user resolution from JWT tokens

### 5. Provider Abstraction System

#### LLM Provider Architecture
The server supports multiple LLM providers through a **strategy pattern**:

```javascript
// From helpers.js
const { getLLMProviderClass } = require("../utils/helpers");
const provider = workspace.chatProvider || process.env.LLM_PROVIDER;
const LLMProvider = getLLMProviderClass({ provider });
```

**Supported Providers**:
- OpenAI, Anthropic, Google Gemini
- Local models (Ollama, LMStudio, LocalAI)
- Cloud providers (AWS Bedrock, Azure OpenAI)
- Open source (Hugging Face, Together AI)

#### Vector Database Abstraction
```javascript
// From helpers.js
const { getVectorDbClass } = require("../utils/helpers");
const VectorDb = getVectorDbClass();
```

**Supported Vector DBs**:
- LanceDB (default), Pinecone, Chroma
- Weaviate, Qdrant, Milvus, Zilliz
- AstraDB, PGVector

### 6. Real-Time Features

#### WebSocket Integration
```javascript
// Conditional WebSocket setup
if (!!process.env.ENABLE_HTTPS) {
  // WebSocket loaded in SSL boot
  require("@mintplex-labs/express-ws").default(app, server);
} else {
  // WebSocket loaded for HTTP
  require("@mintplex-labs/express-ws").default(app);
}
```

**Use Cases**:
- Real-time chat streaming
- Agent workflow execution
- Live document processing status
- System notifications

### 7. Background Services

#### Service Architecture
```javascript
// From boot/index.js
const { BackgroundService } = require("../BackgroundWorkers");
const { EncryptionManager } = require("../EncryptionManager");
const { CommunicationKey } = require("../comKey");

// Service initialization on server boot
new CommunicationKey(true);
new EncryptionManager();
new BackgroundService().boot();
```

**Background Services**:
- **Document sync queues**: Automated document re-processing
- **Telemetry collection**: Anonymous usage analytics
- **Cache management**: Vector cache cleanup and optimization
- **Encryption key management**: Secure data handling

## Notable Technical Decisions

### 1. **Environment-Driven Configuration**
```javascript
// Flexible provider configuration
const llmProvider = process.env.LLM_PROVIDER;
const vectorDB = process.env.VECTOR_DB;
const embeddingEngine = process.env.EMBEDDING_ENGINE ?? "native";
```
**Rationale**: Enables deployment flexibility without code changes

### 2. **Large File Handling**
```javascript
const FILE_LIMIT = "3GB";
app.use(bodyParser.json({ limit: FILE_LIMIT }));
```
**Rationale**: Support for processing large documents and datasets

### 3. **Development vs Production Modes**
```javascript
if (process.env.NODE_ENV !== "development") {
  // Static file serving and security headers in production
  app.use(express.static(path.resolve(__dirname, "public")));
} else {
  // Debug endpoints for vector DB testing
  apiRouter.post("/v/:command", debugVectorHandler);
}
```
**Rationale**: Different behaviors for development debugging vs production security

### 4. **Graceful Error Handling**
```javascript
function catchSigTerms() {
  process.once("SIGUSR2", function () {
    Telemetry.flush();  // Ensure telemetry is sent before shutdown
    process.kill(process.pid, "SIGUSR2");
  });
}
```
**Rationale**: Proper cleanup and data persistence on server shutdown

### 5. **Telemetry and Analytics**
```javascript
// Privacy-focused telemetry
await Telemetry.sendTelemetry("workspace_prompt_changed");
await EventLogs.logEvent("workspace_prompt_changed", metadata, userId);
```
**Rationale**: Product improvement insights while respecting user privacy

This architecture enables AnythingLLM to handle complex document processing workflows, support multiple AI providers, and scale from single-user installations to multi-tenant enterprise deployments.