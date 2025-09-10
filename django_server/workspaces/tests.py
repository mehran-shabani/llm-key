from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import factory
from factory.django import DjangoModelFactory

from .models import (
    Workspace, WorkspaceUser, WorkspaceThread, WorkspaceSuggestedMessage,
    SlashCommandPreset, PromptHistory
)
from authentication.tests import UserFactory


# Factories
class WorkspaceFactory(DjangoModelFactory):
    class Meta:
        model = Workspace
    
    name = factory.Sequence(lambda n: f"Workspace {n}")
    slug = factory.Sequence(lambda n: f"workspace-{n}")
    chat_mode = 'chat'
    chat_provider = 'openai'
    chat_model = 'gpt-4'
    openai_temp = 0.7
    openai_history = 20
    similarity_threshold = 0.25
    top_n = 4


class WorkspaceThreadFactory(DjangoModelFactory):
    class Meta:
        model = WorkspaceThread
    
    name = factory.Sequence(lambda n: f"Thread {n}")
    slug = factory.Sequence(lambda n: f"thread-{n}")
    workspace = factory.SubFactory(WorkspaceFactory)
    user = factory.SubFactory(UserFactory)


class WorkspaceSuggestedMessageFactory(DjangoModelFactory):
    class Meta:
        model = WorkspaceSuggestedMessage
    
    workspace = factory.SubFactory(WorkspaceFactory)
    heading = factory.Faker('sentence', nb_words=3)
    message = factory.Faker('text')


class SlashCommandPresetFactory(DjangoModelFactory):
    class Meta:
        model = SlashCommandPreset
    
    command = factory.Sequence(lambda n: f"/command{n}")
    prompt = factory.Faker('text')
    description = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)


# Model Tests
class WorkspaceModelTest(TestCase):
    def test_workspace_creation(self):
        """Test workspace creation."""
        workspace = WorkspaceFactory()
        self.assertTrue(isinstance(workspace, Workspace))
        self.assertEqual(str(workspace), workspace.name)
    
    def test_workspace_slug_generation(self):
        """Test automatic slug generation."""
        workspace = Workspace.objects.create(name="Test Workspace")
        self.assertEqual(workspace.slug, "test-workspace")
    
    def test_workspace_user_relationship(self):
        """Test workspace-user many-to-many relationship."""
        workspace = WorkspaceFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        
        WorkspaceUser.objects.create(workspace=workspace, user=user1)
        WorkspaceUser.objects.create(workspace=workspace, user=user2)
        
        self.assertEqual(workspace.users.count(), 2)
        self.assertIn(user1, workspace.users.all())
        self.assertIn(user2, workspace.users.all())


class WorkspaceThreadModelTest(TestCase):
    def test_thread_creation(self):
        """Test thread creation."""
        thread = WorkspaceThreadFactory()
        self.assertTrue(isinstance(thread, WorkspaceThread))
        self.assertIn(thread.workspace.name, str(thread))
    
    def test_thread_slug_generation(self):
        """Test automatic thread slug generation."""
        workspace = WorkspaceFactory()
        thread = WorkspaceThread.objects.create(
            name="Test Thread",
            workspace=workspace
        )
        self.assertEqual(thread.slug, "test-thread")


# API Tests
class WorkspaceAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.admin = UserFactory(role='admin')
        self.workspace = WorkspaceFactory()
        
        # Add user to workspace
        WorkspaceUser.objects.create(workspace=self.workspace, user=self.user)
        
        # Get tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
    
    def test_list_workspaces(self):
        """Test listing workspaces."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/workspaces/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_workspace(self):
        """Test workspace creation."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post('/api/workspaces/', {
            'name': 'New Workspace',
            'chat_mode': 'chat',
            'openai_prompt': 'You are a helpful assistant.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Workspace.objects.filter(name='New Workspace').exists()
        )
    
    def test_update_workspace(self):
        """Test workspace update."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.patch(
            f'/api/workspaces/{self.workspace.slug}/',
            {'chat_model': 'gpt-4-turbo'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.chat_model, 'gpt-4-turbo')
    
    def test_workspace_access_control(self):
        """Test workspace access control."""
        other_workspace = WorkspaceFactory()
        
        # User should not see workspace they don't have access to
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/workspaces/')
        workspace_ids = [w['id'] for w in response.data]
        self.assertNotIn(other_workspace.id, workspace_ids)
        
        # Admin should see all workspaces
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/workspaces/')
        workspace_ids = [w['id'] for w in response.data]
        self.assertIn(other_workspace.id, workspace_ids)
    
    def test_add_user_to_workspace(self):
        """Test adding user to workspace."""
        new_user = UserFactory()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post(
            f'/api/workspaces/{self.workspace.slug}/add_user/',
            {'user_id': new_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            WorkspaceUser.objects.filter(
                workspace=self.workspace,
                user=new_user
            ).exists()
        )
    
    def test_remove_user_from_workspace(self):
        """Test removing user from workspace."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post(
            f'/api/workspaces/{self.workspace.slug}/remove_user/',
            {'user_id': self.user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            WorkspaceUser.objects.filter(
                workspace=self.workspace,
                user=self.user
            ).exists()
        )


class WorkspaceThreadAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.workspace = WorkspaceFactory()
        WorkspaceUser.objects.create(workspace=self.workspace, user=self.user)
        
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_thread(self):
        """Test thread creation."""
        response = self.client.post('/api/threads/', {
            'name': 'New Thread',
            'workspace': self.workspace.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            WorkspaceThread.objects.filter(
                name='New Thread',
                user=self.user
            ).exists()
        )
    
    def test_list_threads(self):
        """Test listing threads."""
        thread1 = WorkspaceThreadFactory(workspace=self.workspace, user=self.user)
        thread2 = WorkspaceThreadFactory(workspace=self.workspace, user=None)
        other_thread = WorkspaceThreadFactory(user=UserFactory())
        
        response = self.client.get('/api/threads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        thread_ids = [t['id'] for t in response.data]
        self.assertIn(thread1.id, thread_ids)
        self.assertIn(thread2.id, thread_ids)  # Shared thread
        self.assertNotIn(other_thread.id, thread_ids)  # Other user's thread
    
    def test_get_workspace_threads(self):
        """Test getting threads for a specific workspace."""
        thread = WorkspaceThreadFactory(workspace=self.workspace, user=self.user)
        
        response = self.client.get(f'/api/workspaces/{self.workspace.slug}/threads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], thread.id)


class SlashCommandPresetAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_slash_command(self):
        """Test creating slash command."""
        response = self.client.post('/api/slash-commands/', {
            'command': '/summarize',
            'prompt': 'Summarize the following text:',
            'description': 'Summarizes text'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            SlashCommandPreset.objects.filter(
                command='/summarize',
                user=self.user
            ).exists()
        )
    
    def test_list_slash_commands(self):
        """Test listing slash commands."""
        # User's command
        user_command = SlashCommandPresetFactory(user=self.user)
        
        # Global command
        global_command = SlashCommandPreset.objects.create(
            command='/global',
            prompt='Global prompt',
            description='Global command',
            uid=0
        )
        
        # Other user's command
        other_command = SlashCommandPresetFactory(user=UserFactory())
        
        response = self.client.get('/api/slash-commands/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        command_ids = [c['id'] for c in response.data]
        self.assertIn(user_command.id, command_ids)
        self.assertIn(global_command.id, command_ids)
        self.assertNotIn(other_command.id, command_ids)