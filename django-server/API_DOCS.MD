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
## Documents API

The Documents API provides endpoints for managing document uploads, processing, and organization within the Django application.

### Base URL
All document endpoints are prefixed with `/v1/document/` or `/v1/documents/`

### Authentication
All endpoints require valid API key authentication.

### Endpoints

#### Document Upload
- **POST** `/v1/document/upload/` - Upload a new file to be parsed and prepared for embedding
- **POST** `/v1/document/upload/<folderName>/` - Upload a file to a specific folder
- **POST** `/v1/document/upload-link/` - Upload a document by scraping a URL
- **POST** `/v1/document/raw-text/` - Upload a document by providing raw text content

#### Document Management
- **GET** `/v1/documents/` - List all locally-stored documents
- **GET** `/v1/documents/folder/<folderName>/` - Get documents from a specific folder
- **GET** `/v1/document/<docName>/` - Get a single document by name

#### Document Metadata
- **GET** `/v1/document/accepted-file-types/` - Get accepted file types for upload
- **GET** `/v1/document/metadata-schema/` - Get metadata schema for raw text uploads

#### Folder Management
- **POST** `/v1/document/create-folder/` - Create a new folder in documents storage
- **DELETE** `/v1/document/remove-folder/` - Remove a folder and all its contents
- **POST** `/v1/document/move-files/` - Move files within the documents storage directory

### Django App Structure
- **App**: `apps/documents/`
- **Models**: Document processing and management
- **Serializers**: Request/response validation
- **Views**: API endpoint handlers
- **Storage**: Uses Django FileSystemStorage with configurable root paths

### Configuration
Documents are stored using Django's FileSystemStorage with configurable root paths:
- Development: `/tmp/documents`
- Production: Configurable via `DOCUMENTS_ROOT` setting
<!-- END: DOCUMENTS -->

<!-- BEGIN: FILES -->
## Files API

The Files API provides endpoints for managing file uploads, storage, and organization within the Django application.

### Base URL
All file endpoints are prefixed with `/v1/files/`

### Authentication
All endpoints require valid API key authentication.

### Endpoints

#### File Upload
- **POST** `/v1/files/upload/` - Upload a generic file to files storage
- **POST** `/v1/files/assets/upload/` - Upload an asset file (logos, etc.)
- **POST** `/v1/files/pfp/upload/` - Upload a profile picture

#### File Management
- **GET** `/v1/files/` - List all files in storage
- **GET** `/v1/files/<filename>/` - Get details of a specific file
- **DELETE** `/v1/files/<filename>/delete/` - Delete a specific file
- **POST** `/v1/files/move/` - Move files within storage

#### Storage Information
- **GET** `/v1/files/storage-info/` - Get storage information and usage statistics

### Django App Structure
- **App**: `apps/files/`
- **Storage**: Configurable FileSystemStorage implementations
- **Serializers**: Request/response validation
- **Views**: API endpoint handlers
- **Utilities**: Path normalization and validation functions

### Storage Types
The Files app provides specialized storage classes:
- **ConfigurableFileSystemStorage**: Generic file storage with configurable root
- **DocumentStorage**: Specialized storage for document files
- **AssetStorage**: Specialized storage for asset files (logos, etc.)
- **ProfilePictureStorage**: Specialized storage for profile pictures

### Configuration
Files are stored using Django's FileSystemStorage with configurable root paths:
- **Files**: `/tmp/files` (configurable via `FILES_ROOT`)
- **Documents**: `/tmp/documents` (configurable via `DOCUMENTS_ROOT`)
- **Assets**: `/tmp/assets` (configurable via `ASSETS_ROOT`)
- **Profile Pictures**: `/tmp/assets/pfp` (configurable via `PFP_ROOT`)
- **Vector Cache**: `/tmp/vector-cache` (configurable via `VECTOR_CACHE_ROOT`)
- **Direct Uploads**: `/tmp/direct-uploads` (configurable via `DIRECT_UPLOADS_ROOT`)

### Features
- Path normalization and validation
- Directory existence checking
- File size and metadata tracking
- Batch file operations
- Storage usage statistics
<!-- END: FILES -->

<!-- BEGIN: LLM -->
<!-- END: LLM -->

<!-- BEGIN: EMBEDDING -->
<!-- END: EMBEDDING -->

<!-- BEGIN: IMAGE -->
<!-- END: IMAGE -->

<!-- BEGIN: STT -->
<!-- END: STT -->

<!-- BEGIN: TTS -->
<!-- END: TTS -->

<!-- BEGIN: CONVERSATION -->
<!-- END: CONVERSATION -->

<!-- BEGIN: SCHEMA -->
## API Schema & Documentation

The API schema is automatically generated using DRF Spectacular and provides comprehensive documentation for all available endpoints.

### Available Endpoints

- **OpenAPI Schema**: `/api/schema/` - Raw OpenAPI 3.0 specification
- **Swagger UI**: `/api/docs/` - Interactive API documentation with testing capabilities
- **ReDoc**: `/api/redoc/` - Alternative documentation interface

### Features

- **Interactive Testing**: Test API endpoints directly from the documentation
- **Authentication Support**: Built-in support for Bearer token authentication
- **Dark Theme**: Optional dark mode for better viewing experience
- **Responsive Design**: Mobile-friendly documentation interface
- **Auto-generated**: Schema is automatically updated when API changes

### Usage

1. Navigate to `/api/docs/` for the main Swagger UI interface
2. Use the "Authorize" button to set your API token
3. Explore endpoints by category (Authentication, Admin, System, etc.)
4. Test endpoints directly from the interface

### Schema Configuration

The schema is configured in `apps/api/schema/schema.py` with:
- Common response schemas for authentication errors
- Reusable decorators for authenticated endpoints
- Standardized parameter definitions
- Consistent error response formats

<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
## Background Jobs

The system includes several background jobs for maintenance and synchronization tasks. These jobs have been converted from Node.js to Django management commands.

### Available Jobs

#### 1. cleanup_orphan_documents
Cleans up orphaned files in the direct uploads directory by comparing against known files in the database.

**Usage:**
```bash
python manage.py cleanup_orphan_documents [--batch-size 500] [--dry-run]
```

**Options:**
- `--batch-size`: Number of files to delete in each batch (default: 500)
- `--dry-run`: Show what would be deleted without actually deleting files

#### 2. sync_watched_documents
Syncs watched documents from various sources (links, YouTube, Confluence, GitHub, GitLab, DrupalWiki).

**Usage:**
```bash
python manage.py sync_watched_documents [--max-documents N] [--dry-run]
```

**Options:**
- `--max-documents`: Maximum number of documents to process in this run
- `--dry-run`: Show what would be synced without actually updating documents

#### 3. run_scheduler (Optional)
Runs an automated scheduler using APScheduler to execute the above commands at specified intervals.

**Usage:**
```bash
python manage.py run_scheduler [--cleanup-schedule "0 2 * * *"] [--sync-interval 300]
```

**Options:**
- `--cleanup-schedule`: Cron schedule for cleanup job (default: "0 2 * * *" - daily at 2 AM)
- `--sync-interval`: Interval in seconds for sync job (default: 300 - 5 minutes)

### Manual Scheduling

If you prefer not to use APScheduler, you can schedule these commands using:

**Cron (Linux/macOS):**
```bash
# Cleanup orphaned files daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py cleanup_orphan_documents

# Sync watched documents every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py sync_watched_documents
```

**Windows Task Scheduler:**
Create scheduled tasks to run the management commands at desired intervals.

### Configuration

Required settings in Django settings:
```python
DIRECT_UPLOADS_PATH = '/path/to/direct/uploads'
```

Optional dependencies:
- `apscheduler` - For automated scheduling: `pip install apscheduler`

### Job Dependencies

The jobs require these Django apps:
- `apps.documents` - For document models
- `apps.workspaces` - For workspace models  
- `apps.common` - For shared services (CollectorApi, VectorDB, etc.)
<!-- END: JOBS -->
