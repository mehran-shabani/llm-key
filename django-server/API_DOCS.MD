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
<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
<!-- END: JOBS -->
