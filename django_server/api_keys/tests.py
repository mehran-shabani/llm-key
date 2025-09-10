from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import APIKey, BrowserExtensionAPIKey, Invite
import factory
from factory.django import DjangoModelFactory

User = get_user_model()


class ApiKeyFactory(DjangoModelFactory):
    class Meta:
        model = APIKey
    
    label = factory.Faker('word')
    user = factory.SubFactory('authentication.tests.UserFactory')


class InviteFactory(DjangoModelFactory):
    class Meta:
        model = Invite
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    role = 'default'
    workspace_ids = []
    created_by = factory.SubFactory('authentication.tests.UserFactory')


class ApiKeyTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username=factory.Faker('user_name').generate({}),
            email=factory.Faker('email').generate({}),
            password=factory.Faker('password').generate({}),
            is_staff=True,
            is_superuser=True
        )
        self.user = User.objects.create_user(
            username=factory.Faker('user_name').generate({}),
            email=factory.Faker('email').generate({}),
            password=factory.Faker('password').generate({})
        )
        self.client = APIClient()
    
    def test_create_api_key_admin_only(self):
        """Test that only admins can create API keys."""
        # Non-admin should fail
        self.client.force_authenticate(self.user)
        url = reverse('apikey-list')
        payload = {'label': 'test-key'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin should succeed
        self.client.force_authenticate(self.admin)
        response = self.client.post(url, payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertIn('key', response.data)
    
    def test_list_api_keys(self):
        """Test listing API keys."""
        # Create some API keys
        key1 = ApiKeyFactory(user=self.admin)
        key2 = ApiKeyFactory(user=self.user)
        
        # Admin should see all keys
        self.client.force_authenticate(self.admin)
        url = reverse('apikey-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_api_key(self):
        """Test deleting an API key."""
        key = ApiKeyFactory(user=self.admin)
        
        self.client.force_authenticate(self.admin)
        url = reverse('apikey-detail', kwargs={'pk': key.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify key is deleted
        self.assertFalse(APIKey.objects.filter(id=key.id).exists())


class InviteTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username=factory.Faker('user_name').generate({}),
            email=factory.Faker('email').generate({}),
            password=factory.Faker('password').generate({}),
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
    
    def test_create_invite(self):
        """Test creating an invite."""
        url = reverse('invite-list')
        payload = {
            'name': factory.Faker('name').generate({}),
            'email': factory.Faker('email').generate({}),
            'role': 'default'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('invite_code', response.data)
    
    def test_claim_invite(self):
        """Test claiming an invite."""
        invite = InviteFactory(created_by=self.admin)
        
        # Unauthenticated user claims invite
        self.client.force_authenticate(None)
        url = reverse('invite-claim')
        payload = {
            'invite_code': invite.invite_code,
            'username': factory.Faker('user_name').generate({}),
            'password': factory.Faker('password').generate({}) + '!A1'
        }
        response = self.client.post(url, payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_list_invites(self):
        """Test listing invites."""
        # Create some invites
        InviteFactory(created_by=self.admin)
        InviteFactory(created_by=self.admin, status='accepted')
        
        url = reverse('invite-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get('results', response.data)), 2)
