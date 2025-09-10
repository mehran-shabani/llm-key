# API_DOCS

<!-- BEGIN: AUTH -->
## Authentication Endpoints

### GET /v1/auth
Verify the attached Authentication header contains a valid API token.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "authenticated": true
}
```

**Status Codes:**
- `200` - Valid auth token was found
- `403` - Invalid API key
<!-- END: AUTH -->

<!-- BEGIN: ADMIN -->
## Admin Endpoints

### GET /v1/admin/is-multi-user-mode
Check to see if the instance is in multi-user-mode first. Methods are disabled until multi user mode is enabled via the UI.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "isMultiUser": true
}
```

**Status Codes:**
- `200` - Multi-user mode status
- `403` - Invalid API key

### GET /v1/admin/users
List all users in the system.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "sample-sam",
      "role": "default",
      "suspended": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "last_updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200` - List of users
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/users/new
Create a new user with username and password.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "username": "sample-sam",
  "password": "hunter2",
  "role": "default"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "sample-sam",
    "role": "default"
  },
  "error": null
}
```

**Status Codes:**
- `200` - User created successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/users/{id}
Update existing user settings.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "username": "sample-sam",
  "password": "hunter2",
  "role": "default",
  "suspended": 0
}
```

**Response:**
```json
{
  "success": true,
  "error": null
}
```

**Status Codes:**
- `200` - User updated successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### DELETE /v1/admin/users/{id}
Delete existing user by id.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "success": true,
  "error": null
}
```

**Status Codes:**
- `200` - User deleted successfully
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### GET /v1/admin/invites
List all existing invitations to instance regardless of status.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "invites": [
    {
      "id": 1,
      "code": "abc-123",
      "status": "pending",
      "claimed_by": null,
      "workspace_ids": "1,2,45",
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": 1
    }
  ]
}
```

**Status Codes:**
- `200` - List of invites
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/invite/new
Create a new invite code for someone to use to register with instance.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "workspace_ids": [1, 2, 45]
}
```

**Response:**
```json
{
  "invite": {
    "id": 1,
    "code": "abc-123",
    "status": "pending"
  },
  "error": null
}
```

**Status Codes:**
- `200` - Invite created successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### DELETE /v1/admin/invite/{id}
Deactivates (soft-delete) invite by id.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "success": true,
  "error": null
}
```

**Status Codes:**
- `200` - Invite deactivated successfully
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### GET /v1/admin/workspaces/{workspaceId}/users
Retrieve a list of users with permissions to access the specified workspace.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "users": [
    {
      "userId": 1,
      "username": "main-admin",
      "role": "admin"
    },
    {
      "userId": 2,
      "username": "sample-sam",
      "role": "default"
    }
  ]
}
```

**Status Codes:**
- `200` - List of workspace users
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/workspaces/{workspaceId}/update-users
Overwrite workspace permissions to only be accessible by the given user ids and admins.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "user_ids": [1, 2, 4, 12]
}
```

**Response:**
```json
{
  "success": true,
  "error": null
}
```

**Status Codes:**
- `200` - Workspace users updated successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/workspaces/{workspaceSlug}/manage-users
Set workspace permissions to be accessible by the given user ids and admins.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "user_ids": [1, 2, 4, 12],
  "reset": false
}
```

**Response:**
```json
{
  "success": true,
  "error": null,
  "users": [
    {
      "userId": 1,
      "username": "main-admin",
      "role": "admin"
    },
    {
      "userId": 2,
      "username": "sample-sam",
      "role": "default"
    }
  ]
}
```

**Status Codes:**
- `200` - Workspace users managed successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key

### POST /v1/admin/workspace-chats
All chats in the system ordered by most recent.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "offset": 0
}
```

**Response:**
```json
{
  "chats": [
    {
      "id": 1,
      "workspace_id": 1,
      "prompt": "Hello",
      "response": "Hi there!",
      "include": true,
      "user_id": 1,
      "thread_id": null,
      "api_session_id": null,
      "created_at": "2024-01-01T00:00:00Z",
      "feedback_score": null
    }
  ],
  "has_pages": true
}
```

**Status Codes:**
- `200` - List of workspace chats
- `403` - Invalid API key

### POST /v1/admin/preferences
Update multi-user preferences for instance.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "support_email": "support@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "error": null
}
```

**Status Codes:**
- `200` - Preferences updated successfully
- `400` - Bad request
- `401` - Instance is not in Multi-User mode. Method denied
- `403` - Invalid API key
<!-- END: ADMIN -->

<!-- BEGIN: SYSTEM -->
## System Settings Endpoints

### GET /v1/system/env-dump
Dump all settings to file storage.

**Authentication:** None (but only works in production)

**Response:**
- `200` - Environment dumped successfully

**Status Codes:**
- `200` - Environment dumped successfully
- `403` - Invalid API key

### GET /v1/system
Get all current system settings that are defined.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "settings": {
    "VectorDB": "pinecone",
    "PineConeKey": true,
    "PineConeIndex": "my-pinecone-index",
    "LLMProvider": "azure",
    "[KEY_NAME]": "KEY_VALUE"
  }
}
```

**Status Codes:**
- `200` - System settings retrieved successfully
- `403` - Invalid API key

### GET /v1/system/vector-count
Number of all vectors in connected vector database.

**Authentication:** Required (API Key)

**Response:**
```json
{
  "vectorCount": 5450
}
```

**Status Codes:**
- `200` - Vector count retrieved successfully
- `403` - Invalid API key

### POST /v1/system/update-env
Update a system setting or preference.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "VectorDB": "lancedb",
  "AnotherKey": "updatedValue"
}
```

**Response:**
```json
{
  "newValues": {
    "[ENV_KEY]": "Value"
  },
  "error": "error goes here, otherwise null"
}
```

**Status Codes:**
- `200` - Settings updated successfully
- `400` - Bad request
- `403` - Invalid API key

### GET /v1/system/export-chats
Export all of the chats from the system in a known format. Output depends on the type sent. Will be send with the correct header for the output.

**Authentication:** Required (API Key)

**Query Parameters:**
- `type` (optional): Export format jsonl, json, csv, jsonAlpaca (default: jsonl)

**Response:**
```json
[
  {
    "role": "user",
    "content": "What is AnythinglLM?"
  },
  {
    "role": "assistant",
    "content": "AnythingLLM is a knowledge graph and vector database management system built using NodeJS express server. It provides an interface for handling all interactions, including vectorDB management and LLM (Language Model) interactions."
  }
]
```

**Status Codes:**
- `200` - Chats exported successfully
- `403` - Invalid API key

### DELETE /v1/system/remove-documents
Permanently remove documents from the system.

**Authentication:** Required (API Key)

**Request Body:**
```json
{
  "names": [
    "custom-documents/file.txt-fc4beeeb-e436-454d-8bb4-e5b8979cb48f.json"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Documents removed successfully"
}
```

**Status Codes:**
- `200` - Documents removed successfully
- `400` - Bad request
- `403` - Invalid API key
- `500` - Internal Server Error
<!-- END: SYSTEM -->

<!-- BEGIN: WORKSPACES -->
## Workspace Endpoints

### Create Workspace
- **POST** `/v1/workspace/new/`
- **Description**: Create a new workspace
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "name": "My New Workspace",
    "similarityThreshold": 0.7,
    "openAiTemp": 0.7,
    "openAiHistory": 20,
    "openAiPrompt": "Custom prompt for responses",
    "queryRefusalResponse": "Custom refusal message",
    "chatMode": "chat",
    "topN": 4
  }
  ```
- **Response**:
  ```json
  {
    "workspace": {
      "id": 79,
      "name": "Sample workspace",
      "slug": "sample-workspace",
      "createdAt": "2023-08-17 00:45:03",
      "lastUpdatedAt": "2023-08-17 00:45:03",
      "openAiTemp": null,
      "openAiHistory": 20,
      "openAiPrompt": null
    },
    "message": "Workspace created"
  }
  ```

### List Workspaces
- **GET** `/v1/workspaces/`
- **Description**: List all current workspaces
- **Authentication**: Required (API Key)
- **Response**:
  ```json
  {
    "workspaces": [
      {
        "id": 79,
        "name": "Sample workspace",
        "slug": "sample-workspace",
        "createdAt": "2023-08-17 00:45:03",
        "openAiTemp": null,
        "lastUpdatedAt": "2023-08-17 00:45:03",
        "openAiHistory": 20,
        "openAiPrompt": null,
        "threads": []
      }
    ]
  }
  ```

### Get Workspace
- **GET** `/v1/workspace/{slug}/`
- **Description**: Get a workspace by its unique slug
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace to find
- **Response**:
  ```json
  {
    "workspace": [
      {
        "id": 79,
        "name": "My workspace",
        "slug": "my-workspace-123",
        "createdAt": "2023-08-17 00:45:03",
        "openAiTemp": null,
        "lastUpdatedAt": "2023-08-17 00:45:03",
        "openAiHistory": 20,
        "openAiPrompt": null,
        "documents": [],
        "threads": []
      }
    ]
  }
  ```

### Update Workspace
- **POST** `/v1/workspace/{slug}/update/`
- **Description**: Update workspace settings by its unique slug
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace to find
- **Request Body**:
  ```json
  {
    "name": "Updated Workspace Name",
    "openAiTemp": 0.2,
    "openAiHistory": 20,
    "openAiPrompt": "Respond to all inquires and questions in binary"
  }
  ```

### Delete Workspace
- **DELETE** `/v1/workspace/{slug}/`
- **Description**: Delete a workspace by its slug
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace to delete

### Get Workspace Chats
- **GET** `/v1/workspace/{slug}/chats/`
- **Description**: Get a workspace's chats regardless of user by its unique slug
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace to find
- **Query Parameters**:
  - `apiSessionId` (string, optional): Optional apiSessionId to filter by
  - `limit` (integer, optional): Number of chat messages to return (default: 100)
  - `orderBy` (string, optional): Order of chat messages (asc or desc)

### Update Workspace Embeddings
- **POST** `/v1/workspace/{slug}/update-embeddings/`
- **Description**: Add or remove documents from a workspace by its unique slug
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "adds": ["custom-documents/my-pdf.pdf-hash.json"],
    "deletes": ["custom-documents/anythingllm.txt-hash.json"]
  }
  ```

### Update Document Pin Status
- **POST** `/v1/workspace/{slug}/update-pin/`
- **Description**: Add or remove pin from a document in a workspace by its unique slug
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "docPath": "custom-documents/my-pdf.pdf-hash.json",
    "pinStatus": true
  }
  ```

### Workspace Chat
- **POST** `/v1/workspace/{slug}/chat/`
- **Description**: Execute a chat with a workspace
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "message": "What is AnythingLLM?",
    "mode": "query",
    "sessionId": "identifier-to-partition-chats-by-external-id",
    "attachments": [
      {
        "name": "image.png",
        "mime": "image/png",
        "contentString": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
      }
    ],
    "reset": false
  }
  ```

### Workspace Stream Chat
- **POST** `/v1/workspace/{slug}/stream-chat/`
- **Description**: Execute a streamable chat with a workspace
- **Authentication**: Required (API Key)
- **Content-Type**: `text/event-stream`
- **Request Body**: Same as workspace chat

### Vector Search
- **POST** `/v1/workspace/{slug}/vector-search/`
- **Description**: Perform a vector similarity search in a workspace
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "query": "What is the meaning of life?",
    "topN": 4,
    "scoreThreshold": 0.75
  }
  ```
- **Response**:
  ```json
  {
    "results": [
      {
        "id": "5a6bee0a-306c-47fc-942b-8ab9bf3899c4",
        "text": "Document chunk content...",
        "metadata": {
          "url": "file://document.txt",
          "title": "document.txt",
          "author": "no author specified",
          "description": "no description found",
          "docSource": "post:123456",
          "chunkSource": "document.txt",
          "published": "12/1/2024, 11:39:39 AM",
          "wordCount": 8,
          "tokenCount": 9
        },
        "distance": 0.541887640953064,
        "score": 0.45811235904693604
      }
    ]
  }
  ```
<!-- END: WORKSPACES -->

<!-- BEGIN: CHATS -->
## Chat and Thread Endpoints

### Create Workspace Thread
- **POST** `/v1/workspace/{slug}/thread/new/`
- **Description**: Create a new workspace thread
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
- **Request Body**:
  ```json
  {
    "userId": 1,
    "name": "Thread Name",
    "slug": "thread-slug"
  }
  ```
- **Response**:
  ```json
  {
    "thread": {
      "id": 1,
      "name": "Thread",
      "slug": "thread-uuid",
      "user_id": 1,
      "workspace_id": 1
    },
    "message": null
  }
  ```

### Update Workspace Thread
- **POST** `/v1/workspace/{slug}/thread/{threadSlug}/update/`
- **Description**: Update thread name by its unique slug
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
  - `threadSlug` (string): Unique slug of thread
- **Request Body**:
  ```json
  {
    "name": "Updated Thread Name"
  }
  ```

### Delete Workspace Thread
- **DELETE** `/v1/workspace/{slug}/thread/{threadSlug}/`
- **Description**: Delete a workspace thread
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
  - `threadSlug` (string): Unique slug of thread

### Get Thread Chats
- **GET** `/v1/workspace/{slug}/thread/{threadSlug}/chats/`
- **Description**: Get chats for a workspace thread
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
  - `threadSlug` (string): Unique slug of thread
- **Response**:
  ```json
  {
    "history": [
      {
        "role": "user",
        "content": "What is AnythingLLM?",
        "sentAt": 1692851630
      },
      {
        "role": "assistant",
        "content": "AnythingLLM is a platform that allows you to convert notes, PDFs, and other source materials into a chatbot...",
        "sources": [{"source": "object about source document and snippets used"}]
      }
    ]
  }
  ```

### Chat with Thread
- **POST** `/v1/workspace/{slug}/thread/{threadSlug}/chat/`
- **Description**: Chat with a workspace thread
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
  - `threadSlug` (string): Unique slug of thread
- **Request Body**:
  ```json
  {
    "message": "What is AnythingLLM?",
    "mode": "query",
    "userId": 1,
    "attachments": [
      {
        "name": "image.png",
        "mime": "image/png",
        "contentString": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
      }
    ],
    "reset": false
  }
  ```

### Stream Chat with Thread
- **POST** `/v1/workspace/{slug}/thread/{threadSlug}/stream-chat/`
- **Description**: Stream chat with a workspace thread
- **Authentication**: Required (API Key)
- **Content-Type**: `text/event-stream`
- **Request Body**: Same as thread chat

### Update Chat Content
- **POST** `/v1/workspace/{slug}/update-chat/`
- **Description**: Update chat content
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "chatId": 123,
    "newText": "Updated response text"
  }
  ```

### Chat Feedback
- **POST** `/v1/workspace/{slug}/chat-feedback/{chatId}/`
- **Description**: Update chat feedback
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `slug` (string): Unique slug of workspace
  - `chatId` (integer): ID of the chat
- **Request Body**:
  ```json
  {
    "feedback": "positive"
  }
  ```

### Delete Chats
- **DELETE** `/v1/workspace/{slug}/delete-chats/`
- **Description**: Delete specific chats
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "chatIds": [123, 124, 125]
  }
  ```

### Delete Edited Chats
- **DELETE** `/v1/workspace/{slug}/delete-edited-chats/`
- **Description**: Delete edited chats from a starting point
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "startingId": 100
  }
  ```

### Fork Thread
- **POST** `/v1/workspace/{slug}/thread/fork/`
- **Description**: Fork a thread from a specific chat point
- **Authentication**: Required (API Key)
- **Request Body**:
  ```json
  {
    "chatId": 123,
    "threadSlug": "source-thread-slug"
  }
  ```
- **Response**:
  ```json
  {
    "newThreadSlug": "new-thread-uuid"
  }
  ```

### Hide Chat
- **PUT** `/v1/workspace/workspace-chats/{id}/`
- **Description**: Hide a chat by setting include to false
- **Authentication**: Required (API Key)
- **Path Parameters**:
  - `id` (integer): ID of the chat to hide
- **Response**:
  ```json
  {
    "success": true,
    "error": null
  }
  ```
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
## LLM Endpoints

### POST /api/llm/generate/
Generate text using OpenAI chat completions (category: text_gen).

**Request Body:**
```json
{
  "model": "gpt-4o",  // Optional, defaults to text_gen default
  "messages": [
    {"role": "user", "content": "Hello, world!"}
  ],
  "temperature": 0.7,  // Optional, 0-2
  "max_tokens": 100,   // Optional
  "top_p": 1.0,        // Optional, 0-1
  "frequency_penalty": 0.0,  // Optional, -2 to 2
  "presence_penalty": 0.0,   // Optional, -2 to 2
  "stop": ["\n", "."]  // Optional, list of stop sequences
}
```

**Response:**
```json
{
  "content": "Generated text response",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key

### POST /api/llm/instruct/
Generate text using OpenAI chat completions for instruction following (category: text2text).

**Request Body:**
```json
{
  "model": "gpt-4o-mini",  // Optional, defaults to text2text default
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing"}
  ],
  "temperature": 0.7,  // Optional, 0-2
  "max_tokens": 500,   // Optional
  "top_p": 1.0,        // Optional, 0-1
  "frequency_penalty": 0.0,  // Optional, -2 to 2
  "presence_penalty": 0.0,   // Optional, -2 to 2
  "stop": ["\n\n"]     // Optional, list of stop sequences
}
```

**Response:**
```json
{
  "content": "Detailed explanation of quantum computing...",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 200,
    "total_tokens": 215
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
<!-- END: LLM -->

<!-- BEGIN: EMBEDDING -->
## Embedding Endpoints

### POST /api/embedding/
Generate embedding using OpenAI embeddings API (category: embedding).

**Request Body:**
```json
{
  "model": "text-embedding-3-small",  // Optional, defaults to embedding default
  "input": "Text to generate embedding for",
  "encoding_format": "float"  // Optional, defaults to "float"
}
```

**Response:**
```json
{
  "embedding": [0.1, -0.2, 0.3, ...],  // Array of float values
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
<!-- END: EMBEDDING -->

<!-- BEGIN: IMAGE -->
## Image Endpoints

### POST /api/image/generate/
Generate image using OpenAI images API (category: image).

**Request Body:**
```json
{
  "model": "gpt-image-1",  // Optional, defaults to image default
  "prompt": "A beautiful sunset over mountains",
  "n": 1,                  // Optional, number of images (1-10)
  "size": "1024x1024",     // Optional, image size
  "quality": "standard",  // Optional, "standard" or "hd"
  "style": "vivid",        // Optional, "vivid" or "natural"
  "user": "user123"        // Optional, user identifier
}
```

**Response:**
```json
{
  "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
  "revised_prompt": "A beautiful sunset over mountains with vibrant colors"
}
```

**Headers:**
- `X-OpenAI-Base-URL`: Optional, override OpenAI base URL
- `X-OpenAI-Key`: Optional, override OpenAI API key
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
