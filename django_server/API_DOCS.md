# AnythingLLM API Documentation

Complete REST API documentation for the AnythingLLM Django server.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Obtain tokens via the login endpoint and include them in the Authorization header.

### Obtain Token

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "role": "admin"
  }
}
```

### Refresh Token

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Tokens

Include the access token in all authenticated requests:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 👤 Authentication App

### User Registration

```http
POST /api/users/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!"
}
```

### Get Current User

```http
GET /api/users/me/
Authorization: Bearer <token>
```

### Change Password

```http
POST /api/users/change_password/
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "CurrentPassword123!",
  "new_password": "NewPassword456!",
  "new_password_confirm": "NewPassword456!"
}
```

### Request Password Reset

```http
POST /api/users/request_password_reset/
Content-Type: application/json

{
  "username": "forgetful_user"
}
```

### Reset Password

```http
POST /api/users/reset_password/
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "NewPassword789!",
  "new_password_confirm": "NewPassword789!"
}
```

---

## 📁 Workspaces App

### List Workspaces

```http
GET /api/workspaces/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Workspace",
    "slug": "my-workspace",
    "chat_mode": "chat",
    "chat_provider": "openai",
    "chat_model": "gpt-4",
    "user_count": 5,
    "document_count": 10,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Workspace

```http
POST /api/workspaces/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Workspace",
  "chat_mode": "chat",
  "openai_prompt": "You are a helpful assistant."
}
```

### Update Workspace

```http
PATCH /api/workspaces/{slug}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "chat_model": "gpt-4-turbo",
  "openai_temp": 0.7,
  "top_n": 5
}
```

### Get Workspace Threads

```http
GET /api/workspaces/{slug}/threads/
Authorization: Bearer <token>
```

### Add User to Workspace

```http
POST /api/workspaces/{slug}/add_user/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 2
}
```

---

## 📄 Documents App

### Upload Document

```http
POST /api/documents/upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
workspace_id: 1
metadata: {"source": "manual_upload"}
```

### List Documents

```http
GET /api/documents/?workspace=1&pinned=true
Authorization: Bearer <token>
```

### Pin/Unpin Document

```http
POST /api/documents/{id}/pin/
Authorization: Bearer <token>
Content-Type: application/json

{
  "pin": true
}
```

### Watch Document

```http
POST /api/documents/{id}/watch/
Authorization: Bearer <token>
Content-Type: application/json

{
  "watch": true
}
```

### Bulk Actions

```http
POST /api/documents/bulk_action/
Authorization: Bearer <token>
Content-Type: application/json

{
  "document_ids": [1, 2, 3],
  "action": "pin"  // pin, unpin, watch, unwatch, delete
}
```

---

## 💬 Chats App

### Stream Chat (Server-Sent Events)

```http
POST /api/chats/stream_chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What is the meaning of life?",
  "workspace_slug": "my-workspace",
  "mode": "chat",
  "attachments": []
}
```

**Response (SSE Stream):**
```
data: {"id": "uuid", "type": "start", "message": "Processing..."}
data: {"id": "uuid", "type": "stream", "token": "The "}
data: {"id": "uuid", "type": "stream", "token": "meaning "}
data: {"id": "uuid", "type": "complete", "chat_id": 123}
```

### Get Chat History

```http
GET /api/chats/history/?workspace_id=1&limit=20&offset=0
Authorization: Bearer <token>
```

### Submit Feedback

```http
POST /api/chats/feedback/
Authorization: Bearer <token>
Content-Type: application/json

{
  "chat_id": 123,
  "feedback": true,
  "comment": "Very helpful response!"
}
```

### Export Chats

```http
POST /api/chats/export/
Authorization: Bearer <token>
Content-Type: application/json

{
  "workspace_id": 1,
  "format": "json",  // json, csv, txt, pdf
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-12-31T23:59:59Z"
}
```

### Search Chats

```http
GET /api/chats/search/?query=meaning&workspace_id=1&search_in=prompt,response
Authorization: Bearer <token>
```

### WebSocket Connection

```javascript
// Connect to chat WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat/my-workspace/');

// Send message
ws.send(JSON.stringify({
  type: 'chat',
  message: 'Hello, AI!',
  attachments: []
}));

// Receive streaming response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data);
};
```

---

## 🔌 Embeddings App

### Create Embed Configuration

```http
POST /api/embeddings/configs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "workspace": 1,
  "enabled": true,
  "chat_mode": "query",
  "allowlist_domains": "example.com,app.example.com",
  "max_chats_per_day": 100,
  "message_limit": 20
}
```

### Get Embed Code

```http
GET /api/embeddings/configs/{uuid}/embed_code/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "embed_code": "<script>...</script>",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "workspace": "My Workspace"
}
```

### Toggle Embed

```http
POST /api/embeddings/configs/{uuid}/toggle/
Authorization: Bearer <token>
```

### Get Embed Sessions

```http
GET /api/embeddings/chats/sessions/?embed_config={uuid}
Authorization: Bearer <token>
```

---

## ⚙️ System Settings App

### Get System Status

```http
GET /api/system/status/
Authorization: Bearer <token>
```

**Response:**
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
      "percent": 50.0
    }
  },
  "database": {
    "status": "healthy"
  },
  "settings": {
    "multi_user_mode": true,
    "llm_provider": "openai"
  }
}
```

### Check Setup Complete

```http
GET /api/system/setup-complete/
```

### Update System Setting

```http
PATCH /api/system/settings/{label}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "value": "new_value"
}
```

### View Event Logs

```http
GET /api/system/event-logs/?event=login_event&user_id=1&from_date=2024-01-01
Authorization: Bearer <token>
```

---

## 🔑 API Keys App

### Generate API Key

```http
POST /api/keys/api-keys/generate/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "key": "sk_live_abcdef123456789",
  "id": 1,
  "message": "Save this key securely. It will not be shown again."
}
```

### Verify API Key

```http
POST /api/keys/api-keys/verify/
Content-Type: application/json

{
  "key": "sk_live_abcdef123456789"
}
```

### Generate Browser Extension Key

```http
POST /api/keys/browser-extension-keys/generate/
Authorization: Bearer <token>
```

### Create Invitation

```http
POST /api/keys/invites/generate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "workspace_ids": [1, 2]
}
```

### Claim Invitation

```http
POST /api/keys/invites/claim/
Content-Type: application/json

{
  "code": "INVITE123ABC",
  "username": "newuser",
  "password": "SecurePassword123!",
  "email": "newuser@example.com"
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Validation error message",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests

```json
{
  "error": "You have reached your daily chat limit of 100"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error. Please try again later."
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication**: 5 requests per minute
- **Chat**: Based on user's daily_message_limit
- **Document Upload**: 10 uploads per minute
- **General API**: 100 requests per minute

---

## Pagination

List endpoints support pagination:

```http
GET /api/resource/?limit=20&offset=40
```

Response includes pagination metadata:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/resource/?limit=20&offset=60",
  "previous": "http://localhost:8000/api/resource/?limit=20&offset=20",
  "results": [...]
}
```

---

## Filtering and Searching

Most list endpoints support filtering:

```http
GET /api/chats/?workspace_id=1&thread_id=2&created_at__gte=2024-01-01
```

Search endpoints use the `q` or `query` parameter:

```http
GET /api/workspaces/?search=project
```

---

## WebSocket Events

### Chat WebSocket

**Client → Server:**
- `chat`: Send chat message
- `typing`: Typing indicator
- `feedback`: Rate response

**Server → Client:**
- `chat_start`: Processing started
- `chat_token`: Streaming token
- `chat_complete`: Response complete
- `typing`: User typing status
- `error`: Error message

### Agent WebSocket

**Client → Server:**
- `invoke`: Start agent task
- `tool_response`: Tool execution result
- `close`: End session

**Server → Client:**
- `invocation_started`: Task begun
- `agent_message`: Agent update
- `tool_call`: Tool execution request
- `invocation_closed`: Task complete

---

## API Versioning

The API uses URL-based versioning. Current version: v1

Future versions will be available at:
```
/api/v2/
/api/v3/
```

---

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'user',
    'password': 'pass'
})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
workspaces = requests.get('http://localhost:8000/api/workspaces/', headers=headers)
```

### JavaScript

```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
});
const {access} = await response.json();

// Make authenticated request
const workspaces = await fetch('http://localhost:8000/api/workspaces/', {
  headers: {'Authorization': `Bearer ${access}`}
});
```

### cURL

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' \
  | jq -r '.access')

# Make authenticated request
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/workspaces/
```