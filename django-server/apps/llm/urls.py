from django.urls import path
from . import views

app_name = 'llm'

urlpatterns = [
    path('generate/', views.generate_text, name='generate_text'),
    path('instruct/', views.instruct_text, name='instruct_text'),
]