from django.urls import path
from . import views

app_name = 'conversation'

urlpatterns = [
    path('', views.conversation_view, name='conversation'),
]