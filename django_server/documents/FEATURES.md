# Documents App

## Purpose and Scope
The documents app manages all document-related functionality in AnythingLLM. It handles document upload, storage, vectorization, and synchronization. Documents are the knowledge base that powers the RAG (Retrieval-Augmented Generation) capabilities of the system.

## Key Models

### WorkspaceDocument
- Stores document metadata and references
- Links documents to specific workspaces
- Supports pinning and watching features
- UUID-based document identification

### DocumentVector
- Stores vector embedding references
- Maps document chunks to vector IDs
- Enables semantic search capabilities

### DocumentSyncQueue
- Manages document synchronization schedules
- Tracks watched documents for updates
- Configurable staleness thresholds

### DocumentSyncExecution
- Logs sync execution history
- Tracks sync status and results
- Provides audit trail for document updates

## Key APIs

### Document Management
- `GET /api/documents/` - List workspace documents
- `POST /api/documents/upload/` - Upload new document
- `GET /api/documents/{id}/` - Get document details
- `DELETE /api/documents/{id}/` - Delete document
- `POST /api/documents/{id}/pin/` - Pin/unpin document
- `POST /api/documents/{id}/watch/` - Watch/unwatch document

### Bulk Operations
- `POST /api/documents/bulk_action/` - Perform bulk actions (pin, unpin, watch, unwatch, delete)

### Vector Management
- `GET /api/document-vectors/` - List document vectors
- `POST /api/document-vectors/` - Create vector reference
- `DELETE /api/document-vectors/{id}/` - Delete vector

### Sync Queue
- `GET /api/document-sync-queue/` - List sync queue items
- `POST /api/document-sync-queue/{id}/sync_now/` - Trigger immediate sync

## Technologies/Libraries Used
- **Django file storage**: Document file management
- **UUID**: Unique document identification
- **JSON fields**: Flexible metadata storage
- **Async tasks**: Document processing (ready for Celery integration)

## Architectural Patterns

### Document Storage
- File-based storage with database metadata
- Workspace-isolated document collections
- Support for multiple file formats:
  - Text: .txt, .md, .rtf
  - Documents: .pdf, .doc, .docx, .odt
  - Data: .csv, .json, .xml
  - Spreadsheets: .xls, .xlsx
  - Web: .html

### Vector Integration
- Document chunking for embeddings
- Vector ID mapping for retrieval
- Integration with multiple vector databases:
  - Pinecone
  - Qdrant
  - ChromaDB
  - Weaviate
  - LanceDB

### Document Features
- **Pinning**: Priority documents always included in context
- **Watching**: Automatic synchronization for changes
- **Metadata**: Extensible JSON metadata per document
- **Bulk Actions**: Efficient multi-document operations

### Sync Queue System
- Scheduled document synchronization
- Configurable staleness detection (default 7 days)
- Execution tracking and logging
- Manual sync triggers

### File Upload
- 3GB file size limit
- Multi-part upload support
- File type validation
- Automatic workspace assignment
- Progress tracking capability

## Integration Points
- **Workspaces app**: Documents belong to workspaces
- **Chats app**: Documents provide context for responses
- **Vector databases**: External vector storage systems
- **File processing**: Document parsing and chunking services
- **Storage backend**: Configurable storage (local, S3, etc.)

## Security Features
- Workspace-based access control
- File type validation
- Size limit enforcement
- Secure file storage paths
- User access verification

## Document Processing Pipeline
1. **Upload**: File validation and storage
2. **Parsing**: Extract text content
3. **Chunking**: Split into manageable segments
4. **Embedding**: Generate vector representations
5. **Storage**: Save vectors to database
6. **Indexing**: Make searchable
7. **Sync**: Keep updated if watched

## Supported Operations
- Upload single or multiple documents
- Download original documents
- Search within documents
- Pin important documents
- Watch for changes
- Bulk management
- Metadata tagging
- Version tracking (via sync history)