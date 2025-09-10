# Django CoreDB App - Prisma Migration

This Django app (`apps/coredb`) contains all the data models converted from the Prisma schema (`server/prisma/schema.prisma`) and Node.js models (`server/models/*`).

## Structure

```
django_server/apps/coredb/
├── __init__.py
├── apps.py                    # App configuration
├── models.py                  # All Django models converted from Prisma
├── admin.py                   # Django admin registrations for key models
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py        # Initial migration with all models
└── management/
    └── commands/
        ├── __init__.py
        └── seed.py            # Management command for seeding initial data
```

## Models Converted

All Prisma models have been converted to Django models with proper relationships:

### Core Models
- **User** - Custom user model (extends AbstractUser)
- **Workspace** - Main workspace entity
- **WorkspaceDocument** - Documents within workspaces
- **ApiKey** - API keys for authentication
- **SystemSettings** - System-wide configuration

### Authentication & Security
- **RecoveryCode** - 2FA recovery codes
- **PasswordResetToken** - Password reset tokens
- **TemporaryAuthToken** - Temporary authentication tokens
- **BrowserExtensionApiKey** - Browser extension API keys

### Workspace Features
- **WorkspaceThread** - Chat threads within workspaces
- **WorkspaceChat** - Individual chat messages
- **WorkspaceAgentInvocation** - AI agent invocations
- **WorkspaceUser** - User-workspace relationships
- **WorkspaceSuggestedMessage** - Suggested messages for workspaces
- **WorkspaceParsedFile** - Parsed files in workspaces

### Embedding & External Integration
- **EmbedConfig** - Configuration for embedded widgets
- **EmbedChat** - Chat messages from embedded widgets
- **DocumentVector** - Vector embeddings for documents
- **DocumentSyncQueue** - Document synchronization queue
- **DocumentSyncExecution** - Sync execution logs

### System & Utilities
- **SystemPromptVariable** - System prompt variables
- **PromptHistory** - History of prompt modifications
- **SlashCommandPreset** - Preset slash commands
- **WelcomeMessage** - Welcome messages for users
- **Invite** - User invitation system
- **EventLog** - System event logging
- **CacheData** - Cached data storage
- **DesktopMobileDevice** - Mobile/desktop device connections

## Key Features

### Database Consistency
- All table names match Prisma schema (`db_table` meta option)
- All indexes and constraints preserved
- Foreign key relationships maintained
- Unique constraints and composite keys preserved

### Django Integration
- Custom User model configured in settings
- Django admin interface for key models
- REST Framework ready
- CORS headers configured
- Management command for seeding

### Migration Ready
- Initial migration (`0001_initial.py`) created
- All models properly indexed
- Foreign key relationships established
- Ready for `python manage.py migrate`

## Usage

### Setup
```bash
cd django_server
python manage.py migrate
python manage.py seed  # Seed initial data
python manage.py createsuperuser  # Create admin user
python manage.py runserver
```

### Admin Interface
Access `/admin/` to manage:
- Users and workspaces
- API keys and system settings
- Documents and threads
- Embed configurations
- Event logs and more

### API Ready
The models are ready for Django REST Framework integration with:
- Proper serialization
- Authentication support
- CORS configuration
- Token authentication

## Migration Notes

- **No Vector DB entities** - Only data persisted by the server
- **No extra providers** - Focused on core functionality
- **Consistent naming** - Model names and table names preserved
- **Proper relationships** - All Prisma relations converted to Django ForeignKey/ManyToManyField
- **Index preservation** - All Prisma indexes converted to Django Meta.indexes
- **Constraint mapping** - Unique constraints and composite keys maintained