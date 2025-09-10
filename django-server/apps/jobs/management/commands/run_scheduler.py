"""
APScheduler integration for automated job scheduling.

This module provides optional scheduling capabilities for the Django management commands.
To use APScheduler, install it: pip install apscheduler

Usage:
    python manage.py run_scheduler
"""
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False


class Command(BaseCommand):
    help = 'Run APScheduler to automatically execute background jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-schedule',
            default='0 2 * * *',  # Daily at 2 AM
            help='Cron schedule for cleanup_orphan_documents (default: "0 2 * * *")'
        )
        parser.add_argument(
            '--sync-interval',
            type=int,
            default=300,  # 5 minutes
            help='Interval in seconds for sync_watched_documents (default: 300)'
        )

    def handle(self, *args, **options):
        if not APSCHEDULER_AVAILABLE:
            raise CommandError(
                'APScheduler is not installed. Install it with: pip install apscheduler'
            )
        
        cleanup_schedule = options['cleanup_schedule']
        sync_interval = options['sync_interval']
        
        scheduler = BlockingScheduler()
        
        # Schedule cleanup job
        scheduler.add_job(
            self._run_cleanup_command,
            CronTrigger.from_crontab(cleanup_schedule),
            id='cleanup_orphan_documents',
            name='Cleanup Orphan Documents',
            max_instances=1,
            replace_existing=True
        )
        
        # Schedule sync job
        scheduler.add_job(
            self._run_sync_command,
            IntervalTrigger(seconds=sync_interval),
            id='sync_watched_documents',
            name='Sync Watched Documents',
            max_instances=1,
            replace_existing=True
        )
        
        self.stdout.write(
            self.style.SUCCESS('APScheduler started successfully!')
        )
        self.stdout.write(f'Cleanup job scheduled: {cleanup_schedule}')
        self.stdout.write(f'Sync job interval: {sync_interval} seconds')
        self.stdout.write('Press Ctrl+C to stop the scheduler')
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write('\nScheduler stopped by user')
            scheduler.shutdown()

    def _run_cleanup_command(self):
        """Execute the cleanup_orphan_documents management command"""
        from django.core.management import call_command
        
        try:
            logger.info('Running cleanup_orphan_documents job')
            call_command('cleanup_orphan_documents')
            logger.info('cleanup_orphan_documents job completed successfully')
        except Exception as e:
            logger.error(f'cleanup_orphan_documents job failed: {e}')

    def _run_sync_command(self):
        """Execute the sync_watched_documents management command"""
        from django.core.management import call_command
        
        try:
            logger.info('Running sync_watched_documents job')
            call_command('sync_watched_documents')
            logger.info('sync_watched_documents job completed successfully')
        except Exception as e:
            logger.error(f'sync_watched_documents job failed: {e}')