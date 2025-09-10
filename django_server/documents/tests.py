from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import WorkspaceDocument, DocumentSyncQueue
from workspaces.models import Workspace
import factory
from factory.django import DjangoModelFactory
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class WorkspaceFactory(DjangoModelFactory):
    class Meta:
        model = Workspace
    
    name = factory.Faker('company')
    slug = factory.Faker('slug')


class WorkspaceDocumentFactory(DjangoModelFactory):
    class Meta:
        model = WorkspaceDocument
    
    doc_name = factory.Faker('file_name', extension='pdf')
    doc_path = factory.Faker('file_path')
    workspace = factory.SubFactory(WorkspaceFactory)


class DocumentsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=factory.Faker('user_name').generate({}),
            email=factory.Faker('email').generate({}),
            password=factory.Faker('password').generate({})
        )
        self.workspace = WorkspaceFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_list_documents(self):
        """Test listing workspace documents."""
        # Create some documents
        WorkspaceDocumentFactory(workspace=self.workspace)
        WorkspaceDocumentFactory(workspace=self.workspace)
        
        url = reverse('workspacedocument-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_upload_document(self):
        """Test document upload."""
        url = reverse('workspacedocument-upload')
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"Test file content",
            content_type="text/plain"
        )
        
        payload = {
            'workspace': self.workspace.id,
            'files': [test_file]
        }
        
        response = self.client.post(url, payload, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_pin_document(self):
        """Test pinning a document."""
        doc = WorkspaceDocumentFactory(workspace=self.workspace)
        
        url = reverse('workspacedocument-pin', kwargs={'pk': doc.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        doc.refresh_from_db()
        self.assertTrue(doc.pinned)
    
    def test_unpin_document(self):
        """Test unpinning a document."""
        doc = WorkspaceDocumentFactory(workspace=self.workspace, pinned=True)
        
        url = reverse('workspacedocument-unpin', kwargs={'pk': doc.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        doc.refresh_from_db()
        self.assertFalse(doc.pinned)
    
    def test_delete_document(self):
        """Test deleting a document."""
        doc = WorkspaceDocumentFactory(workspace=self.workspace)
        
        url = reverse('workspacedocument-detail', kwargs={'pk': doc.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify document is deleted
        self.assertFalse(WorkspaceDocument.objects.filter(id=doc.id).exists())


class DocumentSyncTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=factory.Faker('user_name').generate({}),
            email=factory.Faker('email').generate({}),
            password=factory.Faker('password').generate({})
        )
        self.workspace = WorkspaceFactory()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_sync_now(self):
        """Test immediate document sync."""
        doc = WorkspaceDocumentFactory(workspace=self.workspace)
        
        url = reverse('documentsyncqueue-sync-now')
        payload = {'document_id': doc.id}
        response = self.client.post(url, payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_list_sync_queue(self):
        """Test listing sync queue."""
        url = reverse('documentsyncqueue-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
