from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory
import os

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
            # Use environment variable or generate random password
            default_password = os.environ.get('TEST_USER_PASSWORD', factory.Faker('password').generate({}))
            obj.set_password(default_password)


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
        # Use factory with dynamic values
        admin_username = factory.Faker('user_name').generate({})
        admin_password = factory.Faker('password').generate({})
        
        admin = User.objects.create_superuser(
            username=admin_username,
            password=admin_password
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
        # Generate test password dynamically
        self.test_password = factory.Faker('password').generate({})
        self.user = UserFactory(password=self.test_password)
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': self.user.username,
            'password': self.test_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': self.user.username,
            'password': factory.Faker('password').generate({})  # Random wrong password
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh."""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(reverse('token_refresh'), {
            'refresh': str(refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserAPITest(APITestCase):
    def setUp(self):
        # Generate test passwords dynamically
        self.user_password = factory.Faker('password').generate({})
        self.admin_password = factory.Faker('password').generate({})
        
        self.user = UserFactory(password=self.user_password)
        self.admin = UserFactory(role='admin', password=self.admin_password)
        
        # Get tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
    
    def test_user_registration(self):
        """Test user registration."""
        new_username = factory.Faker('user_name').generate({})
        new_email = factory.Faker('email').generate({})
        new_password = factory.Faker('password').generate({}) + '!A1'
        
        response = self.client.post(reverse('user-list'), {
            'username': new_username,
            'email': new_email,
            'password': new_password,
            'password_confirm': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=new_username).exists())
    
    def test_get_current_user(self):
        """Test getting current user info."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get(reverse('user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_change_password(self):
        """Test password change."""
        new_password = factory.Faker('password').generate({}) + '!B2'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post(reverse('user-change-password'), {
            'old_password': self.user_password,
            'new_password': new_password,
            'new_password_confirm': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        
        # Verify can login with new password
        login_response = self.client.post(reverse('token_obtain_pair'), {
            'username': self.user.username,
            'password': new_password
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_request(self):
        """Test password reset request."""
        response = self.client.post(reverse('user-request-password-reset'), {
            'username': self.user.username
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check token was created with valid expiry
        token = PasswordResetToken.objects.filter(user=self.user).first()
        self.assertIsNotNone(token)
        self.assertIsNotNone(token.expires_at)
        self.assertGreater(token.expires_at, timezone.now())
        self.assertLessEqual(token.expires_at, timezone.now() + timedelta(hours=24))
    
    def test_list_users_admin_only(self):
        """Test that only admins can list users."""
        # Non-admin should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin should succeed
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DesktopMobileDeviceAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_device(self):
        """Test device registration."""
        device_name = factory.Faker('catch_phrase').generate({})
        
        response = self.client.post(reverse('desktopmobiledevice-list'), {
            'device_os': 'iOS',
            'device_name': device_name
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            DesktopMobileDevice.objects.filter(
                user=self.user,
                device_name=device_name
            ).exists()
        )
    
    def test_approve_device(self):
        """Test device approval."""
        device = DesktopMobileDevice.objects.create(
            user=self.user,
            device_os='Android',
            device_name=factory.Faker('catch_phrase').generate({}),
            token=factory.Faker('uuid4').generate({})
        )
        
        response = self.client.post(reverse('desktopmobiledevice-approve', kwargs={'pk': device.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        device.refresh_from_db()
        self.assertTrue(device.approved)
    
    def test_revoke_device(self):
        """Test device revocation."""
        device = DesktopMobileDevice.objects.create(
            user=self.user,
            device_os='Android',
            device_name=factory.Faker('catch_phrase').generate({}),
            token=factory.Faker('uuid4').generate({}),
            approved=True
        )
        
        response = self.client.post(reverse('desktopmobiledevice-revoke', kwargs={'pk': device.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        device.refresh_from_db()
        self.assertFalse(device.approved)