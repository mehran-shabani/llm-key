# API_DOCS

<!-- BEGIN: AUTH -->
<!-- END: AUTH -->

<!-- BEGIN: ADMIN -->
<!-- END: ADMIN -->

<!-- BEGIN: SYSTEM -->
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
