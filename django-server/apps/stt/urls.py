from django.urls import path
from . import views

app_name = 'stt'

urlpatterns = [
    path('', views.stt_transcribe, name='transcribe'),
]