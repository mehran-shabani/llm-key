from django.urls import path
from . import views

app_name = 'api_admin'

urlpatterns = [
    path('is-multi-user-mode', views.MultiUserModeView.as_view(), name='multi-user-mode'),
    path('users', views.UsersListView.as_view(), name='users-list'),
    path('users/new', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:user_id>', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:user_id>/delete', views.UserDeleteView.as_view(), name='user-delete'),
    path('invites', views.InvitesListView.as_view(), name='invites-list'),
    path('invite/new', views.InviteCreateView.as_view(), name='invite-create'),
    path('invite/<int:invite_id>', views.InviteDeleteView.as_view(), name='invite-delete'),
    path('workspaces/<int:workspace_id>/users', views.WorkspaceUsersView.as_view(), name='workspace-users'),
    path('workspaces/<int:workspace_id>/update-users', views.WorkspaceUsersUpdateView.as_view(), name='workspace-users-update'),
    path('workspaces/<str:workspace_slug>/manage-users', views.WorkspaceUsersManageView.as_view(), name='workspace-users-manage'),
    path('workspace-chats', views.WorkspaceChatsView.as_view(), name='workspace-chats'),
    path('preferences', views.SystemPreferencesView.as_view(), name='preferences'),
]