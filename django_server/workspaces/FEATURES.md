# Workspaces App

## Purpose and Scope
The workspaces app is the core organizational unit of AnythingLLM. It provides isolated environments for different projects, teams, or use cases. Each workspace has its own configuration, documents, chat history, and user access controls.

## Key Models

### Workspace
- Main organizational unit for chats and documents
- Configurable LLM settings (temperature, model, provider)
- Vector search configuration
- Chat modes: chat vs query
- Custom prompts and responses

### WorkspaceUser
- Many-to-many relationship between users and workspaces
- Manages user access to specific workspaces

### WorkspaceThread
- Conversation threads within workspaces
- Organizes related chat messages
- User-specific or shared threads

### WorkspaceSuggestedMessage
- Pre-configured message suggestions for workspaces
- Helps guide user interactions

### WorkspaceAgentInvocation
- Tracks agent/tool usage within workspaces
- UUID-based identification for async operations
- Supports WebSocket-based agent interactions

### SlashCommandPreset
- Custom slash commands for workspaces
- User-specific or global commands
- Prompt templates and descriptions

### PromptHistory
- Tracks changes to workspace prompts
- Audit trail with user attribution

### WorkspaceParsedFile
- Tracks files parsed and processed in workspaces
- Token count estimation for context management

## Key APIs

### Workspace Management
- `GET /api/workspaces/` - List accessible workspaces
- `POST /api/workspaces/` - Create new workspace
- `GET /api/workspaces/{slug}/` - Get workspace details
- `PATCH /api/workspaces/{slug}/` - Update workspace settings
- `DELETE /api/workspaces/{slug}/` - Delete workspace

### Workspace Features
- `GET /api/workspaces/{slug}/threads/` - List workspace threads
- `GET /api/workspaces/{slug}/suggested_messages/` - Get suggested messages
- `GET /api/workspaces/{slug}/users/` - List workspace users
- `POST /api/workspaces/{slug}/add_user/` - Add user to workspace
- `POST /api/workspaces/{slug}/remove_user/` - Remove user from workspace

### Thread Management
- `GET /api/threads/` - List threads
- `POST /api/threads/` - Create new thread
- `GET /api/threads/{slug}/` - Get thread details
- `DELETE /api/threads/{slug}/` - Delete thread

### Command & History
- `GET /api/slash-commands/` - List slash commands
- `POST /api/slash-commands/` - Create custom command
- `GET /api/prompt-history/` - View prompt history
- `GET /api/parsed-files/` - List parsed files

## Technologies/Libraries Used
- **django-slugify**: URL-friendly workspace identifiers
- **Django ORM**: Complex relationship management
- **JSON fields**: Flexible metadata storage

## Architectural Patterns

### Workspace Isolation
- Each workspace is completely isolated
- Separate document collections
- Independent chat histories
- Workspace-specific configurations

### LLM Configuration
- Per-workspace LLM provider settings
- Configurable models (OpenAI, Anthropic, etc.)
- Temperature and context window settings
- Custom system prompts
- Similarity threshold for RAG

### Access Control
- Role-based workspace access
- Admin can access all workspaces
- Users only see assigned workspaces
- Workspace-specific user permissions

### Thread Organization
- Hierarchical conversation structure
- Workspace > Thread > Chat messages
- User-specific or shared threads
- Thread-based context management

### Agent Integration
- Agent invocation tracking
- UUID-based session management
- WebSocket support for real-time agent interactions
- Tool calling and response handling

### Slash Commands
- Extensible command system
- User-defined shortcuts
- Prompt templates
- Global and user-specific commands

## Integration Points
- **Documents app**: Workspace documents and vectors
- **Chats app**: Chat messages belong to workspaces
- **Embeddings app**: Embed configs tied to workspaces
- **Authentication app**: User access control
- **System Settings**: Event logging and telemetry

## Configuration Options
- **Chat Providers**: OpenAI, Anthropic, Cohere, Ollama
- **Chat Modes**: Standard chat, Query mode
- **Vector Search**: Default, Hybrid modes
- **Agent Providers**: Various AI agent integrations
- **Temperature**: 0.0 to 2.0 for response creativity
- **History**: Number of messages to include in context
- **Top N**: Number of document chunks to retrieve
- **Similarity Threshold**: Minimum similarity for document retrieval