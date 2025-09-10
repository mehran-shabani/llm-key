from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.conf import settings
from django.db import transaction
from apps.coredb.models import User, Invite, Workspace, WorkspaceUser, WorkspaceChat, EventLog, SystemSetting
from .serializers import (
    MultiUserModeSerializer, UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserResponseSerializer, InviteSerializer, InviteCreateSerializer, InviteResponseSerializer,
    WorkspaceUsersResponseSerializer, WorkspaceUsersUpdateSerializer, WorkspaceUsersManageSerializer,
    WorkspaceChatsListSerializer, WorkspaceChatsResponseSerializer, SystemPreferencesSerializer,
    SuccessResponseSerializer
)


def is_multi_user_mode():
    """Check if instance is in multi-user mode"""
    try:
        setting = SystemSetting.objects.get(label='multi_user_mode')
        return setting.value == 'true'
    except SystemSetting.DoesNotExist:
        return False


class MultiUserModeView(APIView):
    """
    Check to see if the instance is in multi-user-mode first.
    Methods are disabled until multi user mode is enabled via the UI.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Check multi-user mode',
        description='Check to see if the instance is in multi-user-mode first. Methods are disabled until multi user mode is enabled via the UI.',
        responses={
            200: OpenApiResponse(
                response=MultiUserModeSerializer,
                description='Multi-user mode status'
            ),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        return Response({'is_multi_user': is_multi_user_mode()})


class UsersListView(APIView):
    """
    List all users in the system
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='List users',
        description='Check to see if the instance is in multi-user-mode first. Methods are disabled until multi user mode is enabled via the UI.',
        responses={
            200: OpenApiResponse(
                response=UserSerializer(many=True),
                description='List of users'
            ),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'users': serializer.data})


class UserCreateView(APIView):
    """
    Create a new user with username and password
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Create user',
        description='Create a new user with username and password. Methods are disabled until multi user mode is enabled via the UI.',
        request=UserCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=UserResponseSerializer,
                description='User created successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({'user': UserSerializer(user).data, 'error': None})
            except Exception as e:
                return Response({'user': None, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'user': None, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    """
    Update existing user settings
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Update user',
        description='Update existing user settings. Methods are disabled until multi user mode is enabled via the UI.',
        request=UserUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=SuccessResponseSerializer,
                description='User updated successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request, user_id):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            user = User.objects.get(id=user_id)
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'error': None})
            return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserDeleteView(APIView):
    """
    Delete existing user by id
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Delete user',
        description='Delete existing user by id. Methods are disabled until multi user mode is enabled via the UI.',
        responses={
            200: OpenApiResponse(
                response=SuccessResponseSerializer,
                description='User deleted successfully'
            ),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def delete(self, request, user_id):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            user.delete()
            
            # Log the event
            EventLog.objects.create(
                event='api_user_deleted',
                metadata=f'{{"userName": "{username}"}}'
            )
            
            return Response({'success': True, 'error': None})
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class InvitesListView(APIView):
    """
    List all existing invitations to instance regardless of status
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='List invites',
        description='List all existing invitations to instance regardless of status. Methods are disabled until multi user mode is enabled via the UI.',
        responses={
            200: OpenApiResponse(
                response=InviteSerializer(many=True),
                description='List of invites'
            ),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        invites = Invite.objects.all()
        serializer = InviteSerializer(invites, many=True)
        return Response({'invites': serializer.data})


class InviteCreateView(APIView):
    """
    Create a new invite code for someone to use to register with instance
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Create invite',
        description='Create a new invite code for someone to use to register with instance. Methods are disabled until multi user mode is enabled via the UI.',
        request=InviteCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=InviteResponseSerializer,
                description='Invite created successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = InviteCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                import uuid
                invite = Invite.objects.create(
                    code=str(uuid.uuid4()),
                    workspace_ids=','.join(map(str, serializer.validated_data.get('workspace_ids', []))),
                    created_by=1  # Assuming admin user ID
                )
                return Response({'invite': InviteSerializer(invite).data, 'error': None})
            except Exception as e:
                return Response({'invite': None, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'invite': None, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class InviteDeleteView(APIView):
    """
    Deactivates (soft-delete) invite by id
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Delete invite',
        description='Deactivates (soft-delete) invite by id. Methods are disabled until multi user mode is enabled via the UI.',
        responses={
            200: OpenApiResponse(
                response=SuccessResponseSerializer,
                description='Invite deactivated successfully'
            ),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def delete(self, request, invite_id):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            invite = Invite.objects.get(id=invite_id)
            invite.status = 'deactivated'
            invite.save()
            return Response({'success': True, 'error': None})
        except Invite.DoesNotExist:
            return Response({'success': False, 'error': 'Invite not found'}, status=status.HTTP_404_NOT_FOUND)


class WorkspaceUsersView(APIView):
    """
    Retrieve a list of users with permissions to access the specified workspace
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Get workspace users',
        description='Retrieve a list of users with permissions to access the specified workspace.',
        responses={
            200: OpenApiResponse(
                response=WorkspaceUsersResponseSerializer,
                description='List of workspace users'
            ),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request, workspace_id):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            workspace_users = WorkspaceUser.objects.filter(workspace_id=workspace_id)
            
            users_data = []
            for wu in workspace_users:
                try:
                    user = User.objects.get(id=wu.user_id)
                    users_data.append({
                        'userId': user.id,
                        'username': user.username,
                        'role': user.role
                    })
                except User.DoesNotExist:
                    continue
                    
            return Response({'users': users_data})
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)


class WorkspaceUsersUpdateView(APIView):
    """
    Overwrite workspace permissions to only be accessible by the given user ids and admins
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Update workspace users (deprecated)',
        description='Overwrite workspace permissions to only be accessible by the given user ids and admins. Methods are disabled until multi user mode is enabled via the UI.',
        request=WorkspaceUsersUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=SuccessResponseSerializer,
                description='Workspace users updated successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        },
        deprecated=True
    )
    def post(self, request, workspace_id):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = WorkspaceUsersUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                workspace = Workspace.objects.get(id=workspace_id)
                user_ids = serializer.validated_data['user_ids']
                
                # Remove all existing users
                WorkspaceUser.objects.filter(workspace_id=workspace_id).delete()
                
                # Add new users
                for user_id in user_ids:
                    WorkspaceUser.objects.create(
                        workspace_id=workspace_id,
                        user_id=user_id
                    )
                
                return Response({'success': True, 'error': None})
            except Workspace.DoesNotExist:
                return Response({'success': False, 'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceUsersManageView(APIView):
    """
    Set workspace permissions to be accessible by the given user ids and admins
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Manage workspace users',
        description='Set workspace permissions to be accessible by the given user ids and admins. Methods are disabled until multi user mode is enabled via the UI.',
        request=WorkspaceUsersManageSerializer,
        responses={
            200: OpenApiResponse(
                response=WorkspaceUsersResponseSerializer,
                description='Workspace users managed successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request, workspace_slug):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = WorkspaceUsersManageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                workspace = Workspace.objects.get(slug=workspace_slug)
                user_ids = serializer.validated_data['user_ids']
                reset = serializer.validated_data.get('reset', False)
                
                # Validate user IDs exist
                valid_user_ids = User.objects.filter(id__in=user_ids).values_list('id', flat=True)
                if not valid_user_ids:
                    return Response({
                        'success': False,
                        'error': 'No valid user IDs provided.',
                        'users': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if reset:
                    # Remove all existing users and add new ones
                    WorkspaceUser.objects.filter(workspace_id=workspace.id).delete()
                    for user_id in valid_user_ids:
                        WorkspaceUser.objects.create(
                            workspace_id=workspace.id,
                            user_id=user_id
                        )
                else:
                    # Add only new users
                    existing_user_ids = WorkspaceUser.objects.filter(
                        workspace_id=workspace.id
                    ).values_list('user_id', flat=True)
                    
                    users_to_add = [uid for uid in valid_user_ids if uid not in existing_user_ids]
                    for user_id in users_to_add:
                        WorkspaceUser.objects.create(
                            workspace_id=workspace.id,
                            user_id=user_id
                        )
                
                # Return updated users list
                workspace_users = WorkspaceUser.objects.filter(workspace_id=workspace.id)
                users_data = []
                for wu in workspace_users:
                    try:
                        user = User.objects.get(id=wu.user_id)
                        users_data.append({
                            'userId': user.id,
                            'username': user.username,
                            'role': user.role
                        })
                    except User.DoesNotExist:
                        continue
                
                return Response({
                    'success': True,
                    'error': None,
                    'users': users_data
                })
                
            except Workspace.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Workspace {workspace_slug} not found',
                    'users': []
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response({
            'success': False,
            'error': 'Invalid data',
            'users': []
        }, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceChatsView(APIView):
    """
    All chats in the system ordered by most recent
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='List workspace chats',
        description='All chats in the system ordered by most recent. Methods are disabled until multi user mode is enabled via the UI.',
        request=WorkspaceChatsListSerializer,
        responses={
            200: OpenApiResponse(
                response=WorkspaceChatsResponseSerializer,
                description='List of workspace chats'
            ),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request):
        serializer = WorkspaceChatsListSerializer(data=request.data)
        if serializer.is_valid():
            offset = serializer.validated_data.get('offset', 0)
            page_size = 20
            
            chats = WorkspaceChat.objects.all().order_by('-id')[offset * page_size:(offset + 1) * page_size]
            total_chats = WorkspaceChat.objects.count()
            has_pages = total_chats > (offset + 1) * page_size
            
            serializer = WorkspaceChatsResponseSerializer({
                'chats': chats,
                'has_pages': has_pages
            })
            return Response(serializer.data)
        
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class SystemPreferencesView(APIView):
    """
    Update multi-user preferences for instance
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Update system preferences',
        description='Update multi-user preferences for instance. Methods are disabled until multi user mode is enabled via the UI.',
        request=SystemPreferencesSerializer,
        responses={
            200: OpenApiResponse(
                response=SuccessResponseSerializer,
                description='Preferences updated successfully'
            ),
            400: OpenApiResponse(description='Bad request'),
            401: OpenApiResponse(description='Instance is not in Multi-User mode. Method denied'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request):
        if not is_multi_user_mode():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = SystemPreferencesSerializer(data=request.data)
        if serializer.is_valid():
            try:
                for key, value in serializer.validated_data.items():
                    setting, created = SystemSetting.objects.get_or_create(label=key)
                    setting.value = str(value)
                    setting.save()
                
                return Response({'success': True, 'error': None})
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)