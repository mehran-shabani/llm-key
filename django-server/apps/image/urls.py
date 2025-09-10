from django.urls import path
from . import views

app_name = 'image'

urlpatterns = [
    path('generate/', views.generate_image, name='generate_image'),
]