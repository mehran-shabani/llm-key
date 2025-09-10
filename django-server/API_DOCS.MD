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
<!-- END: WORKSPACES -->

<!-- BEGIN: CHATS -->
<!-- END: CHATS -->

<!-- BEGIN: DOCUMENTS -->
<!-- END: DOCUMENTS -->

<!-- BEGIN: FILES -->
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
