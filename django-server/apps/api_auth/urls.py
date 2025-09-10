from django.urls import path
from . import views

app_name = 'api_auth'

urlpatterns = [
    path('', views.AuthView.as_view(), name='auth'),
]