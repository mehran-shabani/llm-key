from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from .models import RecoveryCode, PasswordResetToken, TemporaryAuthToken, DesktopMobileDevice

User = get_user_model()


# Factories
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker('email')
    role = 'default'
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if extracted:
            obj.set_password(extracted)
        else:
            obj.set_password('defaultpass123')


class RecoveryCodeFactory(DjangoModelFactory):
    class Meta:
        model = RecoveryCode
    
    user = factory.SubFactory(UserFactory)
    code_hash = factory.Faker('sha256')


class PasswordResetTokenFactory(DjangoModelFactory):
    class Meta:
        model = PasswordResetToken
    
    user = factory.SubFactory(UserFactory)
    token = factory.Faker('uuid4')
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=1))


# Model Tests
class UserModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(str(self.user), self.user.username)
    
    def test_user_can_send_chat_no_limit(self):
        """Test user can send chat when no daily limit is set."""
        self.user.daily_message_limit = None
        self.assertTrue(self.user.can_send_chat())
    
    def test_user_can_send_chat_with_limit(self):
        """Test user chat limit enforcement."""
        self.user.daily_message_limit = 5
        self.assertTrue(self.user.can_send_chat())
    
    def test_superuser_creation(self):
        """Test superuser creation."""
        admin = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'admin')


class RecoveryCodeModelTest(TestCase):
    def test_recovery_code_creation(self):
        """Test recovery code creation."""
        code = RecoveryCodeFactory()
        self.assertIsNotNone(code.code_hash)
        self.assertIsNotNone(code.user)


class PasswordResetTokenModelTest(TestCase):
    def test_token_creation(self):
        """Test password reset token creation."""
        token = PasswordResetTokenFactory()
        self.assertTrue(token.is_valid())
    
    def test_expired_token(self):
        """Test expired token validation."""
        token = PasswordResetTokenFactory(
            expires_at=timezone.now() - timedelta(hours=1)
        )
        self.assertFalse(token.is_valid())


# API Tests
class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory(password='testpass123')
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username,
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh."""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post('/api/auth/refresh/', {
            'refresh': str(refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory(password='testpass123')
        self.admin = UserFactory(role='admin', password='adminpass123')
        
        # Get tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post('/api/users/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_get_current_user(self):
        """Test getting current user info."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_change_password(self):
        """Test password change."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post('/api/users/change_password/', {
            'old_password': 'testpass123',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))
    
    def test_password_reset_request(self):
        """Test password reset request."""
        response = self.client.post('/api/users/request_password_reset/', {
            'username': self.user.username
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            PasswordResetToken.objects.filter(user=self.user).exists()
        )
    
    def test_list_users_admin_only(self):
        """Test that only admins can list users."""
        # Non-admin should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin should succeed
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DesktopMobileDeviceAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_device(self):
        """Test device registration."""
        response = self.client.post('/api/devices/', {
            'device_os': 'iOS',
            'device_name': 'iPhone 15'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            DesktopMobileDevice.objects.filter(
                user=self.user,
                device_name='iPhone 15'
            ).exists()
        )
    
    def test_approve_device(self):
        """Test device approval."""
        device = DesktopMobileDevice.objects.create(
            user=self.user,
            device_os='Android',
            device_name='Pixel 8',
            token='test_token'
        )
        
        response = self.client.post(f'/api/devices/{device.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        device.refresh_from_db()
        self.assertTrue(device.approved)
    
    def test_revoke_device(self):
        """Test device revocation."""
        device = DesktopMobileDevice.objects.create(
            user=self.user,
            device_os='Android',
            device_name='Pixel 8',
            token='test_token',
            approved=True
        )
        
        response = self.client.post(f'/api/devices/{device.id}/revoke/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        device.refresh_from_db()
        self.assertFalse(device.approved)