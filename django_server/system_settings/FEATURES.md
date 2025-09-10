# System Settings App

## Purpose and Scope
The system_settings app manages global system configuration, event logging, telemetry, caching, and system monitoring. It provides centralized configuration management and comprehensive audit logging for the entire AnythingLLM platform.

## Key Models

### SystemSetting
- Key-value store for system configuration
- Cached for performance
- Dynamic configuration updates
- No restart required for changes

### SystemPromptVariable
- Customizable prompt variables
- System, user, and dynamic types
- Template variable substitution
- User-specific customization

### EventLog
- Comprehensive audit logging
- User action tracking
- System event recording
- Searchable and filterable

### Telemetry
- Anonymous usage statistics
- Feature adoption tracking
- Performance metrics
- Optional data collection

### CacheData
- Application-level caching
- Expiration support
- Named cache entries
- Flexible data storage

## Key APIs

### System Configuration
- `GET /api/system/settings/` - List all settings
- `GET /api/system/settings/{label}/` - Get specific setting
- `PATCH /api/system/settings/{label}/` - Update setting
- `GET /api/system/status/` - System health and metrics
- `GET /api/system/setup-complete/` - Check setup status

### Prompt Variables
- `GET /api/system/prompt-variables/` - List variables
- `POST /api/system/prompt-variables/` - Create variable
- `PATCH /api/system/prompt-variables/{key}/` - Update variable

### Logging & Monitoring
- `GET /api/system/event-logs/` - View event logs
- `GET /api/system/telemetry/` - View telemetry data
- `GET /api/system/cache/` - Manage cache entries

## Technologies/Libraries Used
- **Django cache framework**: High-performance caching
- **psutil**: System resource monitoring
- **platform**: System information
- **JSON fields**: Flexible data storage
- **Django signals**: Event-driven updates

## Architectural Patterns

### Configuration Management
- **Dynamic Settings**: Runtime configuration changes
- **Cached Values**: 5-minute cache TTL
- **Type Safety**: Validated setting values
- **Default Values**: Fallback configurations
- **Environment Override**: ENV vars take precedence

### Event Logging System
- **Event Types**: Categorized events
- **Metadata Storage**: JSON context data
- **User Attribution**: Track who did what
- **Timestamp Tracking**: When events occurred
- **Query Capabilities**: Filter and search logs

### Telemetry Collection
- **Opt-in/Opt-out**: Configurable data collection
- **Anonymous Data**: No PII collected
- **Event-based**: Specific action tracking
- **Aggregated Metrics**: Usage patterns
- **Performance Data**: Response times, errors

### Cache Management
- **Named Entries**: Organized cache keys
- **Expiration**: TTL-based invalidation
- **Ownership**: Track cache creators
- **Bulk Operations**: Clear by pattern
- **Statistics**: Cache hit/miss rates

### System Monitoring
- **Resource Usage**: CPU, memory, disk
- **Database Health**: Connection status
- **Application Status**: Version, environment
- **Configuration Status**: LLM, embedding, vector DB
- **Real-time Metrics**: Current system state

## Event Categories

### Authentication Events
- login_event
- logout_event
- failed_login_invalid_username
- failed_login_invalid_password
- failed_login_account_suspended
- password_changed
- password_reset_requested
- recovery_codes_generated

### Workspace Events
- workspace_created
- workspace_updated
- workspace_deleted
- workspace_user_added
- workspace_user_removed

### Document Events
- document_uploaded
- document_deleted
- document_pinned
- document_watched
- document_sync_triggered

### Chat Events
- chat_sent
- websocket_chat_sent
- chat_feedback
- chat_exported

### System Events
- system_setting_changed
- api_key_generated
- invite_generated
- invite_claimed

## System Status Information
```json
{
  "status": "online",
  "version": "1.0.0",
  "environment": "production",
  "system": {
    "platform": "Linux",
    "cpu_percent": 25.5,
    "memory": {
      "total": 8589934592,
      "available": 4294967296,
      "percent": 50.0
    },
    "disk": {
      "total": 107374182400,
      "free": 53687091200,
      "percent": 50.0
    }
  },
  "database": {
    "status": "healthy",
    "engine": "postgresql"
  },
  "settings": {
    "multi_user_mode": true,
    "telemetry_enabled": false,
    "llm_provider": "openai",
    "embedding_engine": "openai",
    "vector_db": "pinecone"
  }
}
```

## Integration Points
- **All apps**: Event logging for audit trail
- **Authentication**: User tracking for events
- **Configuration**: System-wide settings
- **Monitoring**: Health checks and metrics
- **Caching**: Performance optimization

## Performance Features
- **Cached Settings**: Reduce database queries
- **Bulk Logging**: Batch event writes
- **Async Telemetry**: Non-blocking data collection
- **Efficient Queries**: Indexed event searches
- **Resource Monitoring**: Prevent system overload

## Security Features
- **Audit Trail**: Complete action history
- **Admin-only Access**: Restricted configuration
- **Sensitive Data**: Encrypted storage
- **Rate Limiting**: Via cache tracking
- **Access Logging**: Track system access

## Setup Validation
- Check for admin user
- Verify LLM configuration
- Validate vector database
- Ensure required settings
- Guide initial setup