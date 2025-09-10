# Chats App

## Purpose and Scope
The chats app is the heart of AnythingLLM's conversational AI functionality. It manages all chat interactions, streaming responses, WebSocket connections, and chat history. The app provides both REST APIs and WebSocket interfaces for real-time communication.

## Key Models

### WorkspaceChat
- Stores all chat messages (prompts and responses)
- Links to workspace, user, and thread
- Supports feedback scoring
- Includes flag for context inclusion
- API session tracking for external integrations

### WelcomeMessage
- Customizable welcome messages for users
- Ordered display capability
- User-specific greetings

## Key APIs

### REST Endpoints
- `GET /api/chats/` - List chat history
- `POST /api/chats/stream_chat/` - Stream chat response (SSE)
- `GET /api/chats/history/` - Filtered chat history
- `POST /api/chats/feedback/` - Submit chat feedback
- `POST /api/chats/export/` - Export chat history
- `GET /api/chats/search/` - Search through chats

### WebSocket Endpoints
- `ws/chat/{workspace_slug}/` - Real-time chat connection
- `ws/agent/{workspace_slug}/` - Agent interaction connection

### Welcome Messages
- `GET /api/welcome-messages/` - List welcome messages
- `POST /api/welcome-messages/` - Create welcome message

## Technologies/Libraries Used
- **Django Channels**: WebSocket support
- **Server-Sent Events (SSE)**: Streaming responses
- **Redis**: WebSocket channel layer
- **AsyncIO**: Asynchronous message handling
- **JSON streaming**: Token-by-token response delivery

## Architectural Patterns

### Streaming Architecture
- **Server-Sent Events**: HTTP-based streaming for REST clients
- **WebSockets**: Full-duplex communication for real-time chat
- **Token Streaming**: Character or word-level streaming
- **Chunked Responses**: Efficient memory usage for long responses

### Chat Modes
- **Standard Chat**: Conversational with context
- **Query Mode**: Single-turn question answering
- **Thread-based**: Organized conversations
- **API Sessions**: External integration tracking

### WebSocket Features
- **Real-time messaging**: Instant message delivery
- **Typing indicators**: Show when users are typing
- **Connection management**: Automatic reconnection
- **Room-based isolation**: Workspace-specific channels
- **Authentication**: JWT-based WebSocket auth

### Agent Integration
- **Tool calling**: Interactive agent capabilities
- **Streaming responses**: Real-time agent feedback
- **Session management**: UUID-based invocation tracking
- **Tool response handling**: Client-side tool execution

### Chat Features
- **Message History**: Complete conversation tracking
- **Context Management**: Include/exclude from context
- **Feedback System**: Positive/negative ratings
- **Export Capabilities**: JSON, CSV, TXT, PDF formats
- **Search Functionality**: Full-text search in prompts/responses
- **Rate Limiting**: Daily message limits per user

## WebSocket Protocol

### Message Types
```json
// Client -> Server
{
  "type": "chat",
  "message": "User message",
  "attachments": []
}

{
  "type": "typing",
  "is_typing": true
}

{
  "type": "feedback",
  "chat_id": 123,
  "feedback": true
}

// Server -> Client
{
  "type": "chat_start",
  "chat_id": "uuid",
  "message": "Processing..."
}

{
  "type": "chat_token",
  "chat_id": "uuid",
  "token": "word"
}

{
  "type": "chat_complete",
  "chat_id": "uuid",
  "db_id": 123,
  "response": "Full response"
}
```

## Integration Points
- **Workspaces app**: Chats belong to workspaces
- **Documents app**: Context from documents
- **LLM Providers**: OpenAI, Anthropic, Cohere, etc.
- **Vector Search**: RAG implementation
- **Authentication**: User-based chat tracking
- **System Settings**: Event logging and telemetry

## Chat Processing Pipeline
1. **Input Validation**: Message content and length checks
2. **Rate Limiting**: Check user daily limits
3. **Context Building**: Gather relevant documents and history
4. **LLM Processing**: Send to configured provider
5. **Response Streaming**: Token-by-token delivery
6. **Storage**: Save to database
7. **Telemetry**: Log events and metrics

## Export Formats
- **JSON**: Complete structured data
- **CSV**: Tabular format for analysis
- **TXT**: Plain text conversation
- **PDF**: Formatted document (planned)

## Search Capabilities
- Search in prompts
- Search in responses
- Combined search
- Workspace filtering
- Thread filtering
- Date range filtering

## Performance Optimizations
- Streaming responses for better UX
- Chunked database queries
- Redis-based WebSocket scaling
- Async processing
- Connection pooling
- Message queuing for high load