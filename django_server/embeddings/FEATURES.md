# Embeddings App

## Purpose and Scope
The embeddings app manages embedded chat widgets that can be integrated into external websites. It provides configurable, secure, and isolated chat interfaces that can be embedded via JavaScript snippets while maintaining workspace isolation and security.

## Key Models

### EmbedConfig
- Configuration for embedded chat widgets
- UUID-based identification
- Domain whitelisting for security
- Rate limiting and session controls
- Override permissions for model/temperature/prompt

### EmbedChat
- Chat messages from embedded widgets
- Session-based conversation tracking
- Connection information logging
- Separate from main workspace chats

## Key APIs

### Configuration Management
- `GET /api/embeddings/configs/` - List embed configurations
- `POST /api/embeddings/configs/` - Create new embed config
- `GET /api/embeddings/configs/{uuid}/` - Get config details
- `PATCH /api/embeddings/configs/{uuid}/` - Update config
- `POST /api/embeddings/configs/{uuid}/toggle/` - Enable/disable embed
- `GET /api/embeddings/configs/{uuid}/embed_code/` - Generate embed code

### Embed Chat Management
- `GET /api/embeddings/chats/` - List embed chats
- `GET /api/embeddings/chats/sessions/` - Get unique sessions
- `POST /api/embeddings/chats/` - Create chat (usually via widget)

## Technologies/Libraries Used
- **UUID**: Secure embed identification
- **CORS**: Cross-origin resource sharing
- **Domain validation**: Security whitelisting
- **Session management**: Conversation tracking
- **JavaScript SDK**: Embed widget implementation

## Architectural Patterns

### Security Model
- **Domain Whitelisting**: Restrict embed usage to specific domains
- **UUID-based Access**: No workspace details exposed
- **Session Isolation**: Separate sessions per visitor
- **Rate Limiting**: Per-day and per-session limits
- **CORS Protection**: Prevent unauthorized embedding

### Configuration Options
- **Chat Mode**: Query or conversational
- **Model Override**: Allow embedded widget to change model
- **Temperature Override**: Adjustable response creativity
- **Prompt Override**: Custom system prompts
- **Message Limits**: Control conversation length
- **Daily Limits**: Prevent abuse

### Embed Widget Features
- **Responsive Design**: Mobile and desktop compatible
- **Customizable UI**: Theming options
- **Session Persistence**: Continue conversations
- **Async Loading**: Non-blocking page load
- **Error Handling**: Graceful degradation

### Session Management
- **Unique Sessions**: UUID per visitor
- **Session Persistence**: Cookie or localStorage
- **Session Statistics**: Track usage metrics
- **Connection Info**: IP, user agent, referrer

## Integration Points
- **Workspaces app**: Embeds tied to specific workspaces
- **Chats app**: Shares chat infrastructure
- **Authentication**: Creator tracking
- **System Settings**: Event logging

## Embed Code Generation
```html
<script>
  (function() {
    var script = document.createElement('script');
    script.src = 'https://your-domain.com/static/embed.js';
    script.setAttribute('data-embed-id', 'uuid-here');
    script.setAttribute('data-base-url', 'https://your-domain.com/');
    document.head.appendChild(script);
  })();
</script>
<div id="anythingllm-embed-uuid-here"></div>
```

## Widget Communication Protocol
- **Initialization**: Widget loads and authenticates
- **Message Sending**: POST to embed chat endpoint
- **Response Streaming**: SSE or polling
- **Error Handling**: Retry logic and fallbacks
- **Session Management**: Automatic session creation

## Rate Limiting Strategy
- **Per-Session Limits**: Maximum chats per session
- **Daily Limits**: Maximum chats per day across all sessions
- **Message Limits**: Maximum messages per conversation
- **Throttling**: Prevent rapid-fire requests

## Analytics and Tracking
- **Session Count**: Unique visitors
- **Chat Volume**: Messages per embed
- **Domain Usage**: Which sites use embeds
- **Performance Metrics**: Response times
- **Error Rates**: Failed requests

## Security Considerations
- **XSS Protection**: Sanitized inputs/outputs
- **CSRF Protection**: Token validation
- **Domain Validation**: Prevent unauthorized usage
- **Rate Limiting**: Prevent abuse
- **Data Isolation**: No cross-workspace access
- **Secure Communication**: HTTPS only

## Customization Options
- **Branding**: Custom colors and logos
- **Welcome Messages**: Personalized greetings
- **Suggested Prompts**: Guide user interactions
- **Language Support**: Multi-language capability
- **Timezone Handling**: Local time display

## Performance Optimizations
- **Lazy Loading**: Load widget on demand
- **CDN Distribution**: Fast global delivery
- **Minified Assets**: Reduced payload size
- **Caching**: Response caching where appropriate
- **Connection Pooling**: Efficient resource usage