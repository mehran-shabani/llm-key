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
