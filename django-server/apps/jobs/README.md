# Jobs App

This Django app contains background jobs converted from the original Node.js `server/jobs/*` files.

## Management Commands

### 1. cleanup_orphan_documents

Cleans up orphaned files in the direct uploads directory by comparing against known files in the database.

```bash
# Basic usage
python manage.py cleanup_orphan_documents

# With custom batch size
python manage.py cleanup_orphan_documents --batch-size 1000

# Dry run to see what would be deleted
python manage.py cleanup_orphan_documents --dry-run
```

**Options:**
- `--batch-size`: Number of files to delete in each batch (default: 500)
- `--dry-run`: Show what would be deleted without actually deleting files

### 2. sync_watched_documents

Syncs watched documents from various sources (links, YouTube, Confluence, GitHub, GitLab, DrupalWiki).

```bash
# Basic usage
python manage.py sync_watched_documents

# Process limited number of documents
python manage.py sync_watched_documents --max-documents 10

# Dry run to see what would be synced
python manage.py sync_watched_documents --dry-run
```

**Options:**
- `--max-documents`: Maximum number of documents to process in this run
- `--dry-run`: Show what would be synced without actually updating documents

### 3. run_scheduler (Optional APScheduler)

Runs an automated scheduler to execute the above commands at specified intervals.

```bash
# Install APScheduler first
pip install apscheduler

# Run with default schedules
python manage.py run_scheduler

# Custom schedules
python manage.py run_scheduler --cleanup-schedule "0 3 * * *" --sync-interval 600
```

**Options:**
- `--cleanup-schedule`: Cron schedule for cleanup job (default: "0 2 * * *" - daily at 2 AM)
- `--sync-interval`: Interval in seconds for sync job (default: 300 - 5 minutes)

## Manual Scheduling

If you prefer not to use APScheduler, you can schedule these commands using:

### Cron (Linux/macOS)
```bash
# Add to crontab (crontab -e)
# Cleanup orphaned files daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py cleanup_orphan_documents

# Sync watched documents every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py sync_watched_documents
```

### Windows Task Scheduler
Create scheduled tasks to run the management commands at desired intervals.

### Docker/Cron
```dockerfile
# In your Dockerfile or docker-compose.yml
# Add cron jobs for containerized environments
```

## Configuration

Make sure these settings are configured in your Django settings:

```python
# settings.py
DIRECT_UPLOADS_PATH = '/path/to/direct/uploads'

# Logging configuration for jobs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/jobs.log',
        },
    },
    'loggers': {
        'apps.jobs': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Dependencies

The jobs require these Django apps to be installed:
- `apps.documents` - For document models
- `apps.workspaces` - For workspace models  
- `apps.common` - For shared services (CollectorApi, VectorDB, etc.)

Optional:
- `apscheduler` - For automated scheduling