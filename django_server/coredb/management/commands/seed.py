from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from coredb.models import (
    Workspace, SystemSettings, ApiKey, WorkspaceDocument,
    WorkspaceThread, WorkspaceSuggestedMessage, EmbedConfig
)
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')
        
        # Create default admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create default workspace
        workspace, created = Workspace.objects.get_or_create(
            slug='default-workspace',
            defaults={
                'name': 'Default Workspace',
                'openai_temp': 0.7,
                'openai_history': 20,
                'similarity_threshold': 0.25,
                'top_n': 4,
                'chat_mode': 'chat',
                'vector_search_mode': 'default',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created default workspace'))
        else:
            self.stdout.write('Default workspace already exists')
        
        # Create system settings
        default_settings = [
            ('app_name', 'AnythingLLM'),
            ('app_logo', ''),
            ('vector_db', 'pinecone'),
            ('openai_api_key', ''),
            ('openai_model_preference', 'gpt-3.5-turbo'),
            ('embedding_engine', 'openai'),
            ('embedding_model', 'text-embedding-ada-002'),
            ('max_upload_size', '15000000'),
            ('max_document_count', '50'),
            ('enable_custom_instructions', 'true'),
            ('enable_web_search', 'false'),
            ('enable_rag', 'true'),
        ]
        
        for label, value in default_settings:
            setting, created = SystemSettings.objects.get_or_create(
                label=label,
                defaults={'value': value}
            )
            if created:
                self.stdout.write(f'Created system setting: {label}')
        
        # Create API key for admin
        api_key, created = ApiKey.objects.get_or_create(
            created_by=admin_user,
            defaults={'secret': f'ak-{uuid.uuid4().hex[:32]}'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created API key for admin'))
        
        # Create sample workspace thread
        thread, created = WorkspaceThread.objects.get_or_create(
            slug='sample-thread',
            workspace=workspace,
            defaults={
                'name': 'Sample Thread',
                'user': admin_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created sample thread'))
        
        # Create sample suggested messages
        suggested_messages = [
            ('Welcome', 'Hello! How can I help you today?'),
            ('Documentation', 'Can you help me understand this document?'),
            ('Summary', 'Please provide a summary of the key points'),
        ]
        
        for heading, message in suggested_messages:
            suggested_msg, created = WorkspaceSuggestedMessage.objects.get_or_create(
                workspace=workspace,
                heading=heading,
                defaults={'message': message}
            )
            if created:
                self.stdout.write(f'Created suggested message: {heading}')
        
        # Create embed config
        embed_config, created = EmbedConfig.objects.get_or_create(
            workspace=workspace,
            defaults={
                'uuid': str(uuid.uuid4()),
                'enabled': True,
                'chat_mode': 'query',
                'message_limit': 20,
                'created_by': admin_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created embed config'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))