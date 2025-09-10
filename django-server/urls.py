from django.urls import path, include

urlpatterns = [
    path('api/llm/', include('apps.llm.urls')),
    path('api/embedding/', include('apps.embedding.urls')),
    path('api/image/', include('apps.image.urls')),
]