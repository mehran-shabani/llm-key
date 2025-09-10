from django.urls import path
from . import views

app_name = 'embedding'

urlpatterns = [
    path('', views.generate_embedding, name='generate_embedding'),
]