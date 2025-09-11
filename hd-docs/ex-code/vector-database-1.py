# Feature: Multiple Vector Database Support
# Description: Pluggable vector database architecture supporting multiple providers
# Library: Django, pinecone-client, chromadb, qdrant-client, numpy

# 1. models.py - Vector database configuration
from django.db import models
import json

class VectorDatabase(models.Model):
    PROVIDER_CHOICES = [
        ('lancedb', 'LanceDB'),
        ('pinecone', 'Pinecone'),
        ('chroma', 'Chroma'),
        ('qdrant', 'Qdrant'),
        ('weaviate', 'Weaviate'),
        ('milvus', 'Milvus'),
        ('pgvector', 'PGVector'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    connection_config = models.JSONField()  # Provider-specific config
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    embedding_dimension = models.IntegerField(default=1536)
    distance_metric = models.CharField(max_length=20, default='cosine')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VectorNamespace(models.Model):
    database = models.ForeignKey(VectorDatabase, on_delete=models.CASCADE, related_name='namespaces')
    name = models.CharField(max_length=100)
    vector_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('database', 'name')

# 2. vector_providers.py - Vector database provider implementations
import numpy as np
from abc import ABC, abstractmethod
import uuid
from typing import List, Dict, Any, Optional

class BaseVectorProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
    
    @abstractmethod
    async def connect(self):
        """Establish connection to vector database"""
        pass
    
    @abstractmethod
    async def create_namespace(self, namespace: str, dimension: int = 1536):
        """Create a new namespace/collection"""
        pass
    
    @abstractmethod
    async def delete_namespace(self, namespace: str):
        """Delete a namespace/collection"""
        pass
    
    @abstractmethod
    async def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]):
        """Insert or update vectors"""
        pass
    
    @abstractmethod
    async def similarity_search(self, namespace: str, query_vector: List[float], 
                              top_k: int = 5, similarity_threshold: float = 0.7):
        """Perform similarity search"""
        pass
    
    @abstractmethod
    async def delete_vectors(self, namespace: str, vector_ids: List[str]):
        """Delete vectors by IDs"""
        pass
    
    @abstractmethod
    async def get_namespace_stats(self, namespace: str):
        """Get namespace statistics"""
        pass
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class PineconeProvider(BaseVectorProvider):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.environment = config.get('environment')
        self.index_name = config.get('index_name')
    
    async def connect(self):
        try:
            import pinecone
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Check if index exists
            if self.index_name not in pinecone.list_indexes():
                raise Exception(f"Index {self.index_name} does not exist")
            
            self.client = pinecone.Index(self.index_name)
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to Pinecone: {str(e)}")
    
    async def create_namespace(self, namespace: str, dimension: int = 1536):
        # Pinecone uses namespaces within an index
        return True
    
    async def delete_namespace(self, namespace: str):
        if self.client:
            self.client.delete(delete_all=True, namespace=namespace)
            return True
        return False
    
    async def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]):
        if not self.client:
            await self.connect()
        
        # Format vectors for Pinecone
        pinecone_vectors = []
        for vector in vectors:
            pinecone_vectors.append({
                'id': vector['id'],
                'values': vector['values'],
                'metadata': vector.get('metadata', {})
            })
        
        # Batch upsert (Pinecone has limits on batch size)
        batch_size = 100
        for i in range(0, len(pinecone_vectors), batch_size):
            batch = pinecone_vectors[i:i + batch_size]
            self.client.upsert(vectors=batch, namespace=namespace)
        
        return len(pinecone_vectors)
    
    async def similarity_search(self, namespace: str, query_vector: List[float], 
                              top_k: int = 5, similarity_threshold: float = 0.7):
        if not self.client:
            await self.connect()
        
        response = self.client.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )
        
        results = []
        for match in response['matches']:
            if match['score'] >= similarity_threshold:
                results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {}),
                    'content': match['metadata'].get('content', '')
                })
        
        return results
    
    async def delete_vectors(self, namespace: str, vector_ids: List[str]):
        if not self.client:
            await self.connect()
        
        self.client.delete(ids=vector_ids, namespace=namespace)
        return True
    
    async def get_namespace_stats(self, namespace: str):
        if not self.client:
            await self.connect()
        
        stats = self.client.describe_index_stats()
        namespace_stats = stats.get('namespaces', {}).get(namespace, {})
        
        return {
            'vector_count': namespace_stats.get('vector_count', 0),
            'dimension': stats.get('dimension', 0)
        }

class ChromaProvider(BaseVectorProvider):
    def __init__(self, config):
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8000)
    
    async def connect(self):
        try:
            import chromadb
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            # Test connection
            self.client.heartbeat()
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to Chroma: {str(e)}")
    
    def _normalize_collection_name(self, name: str) -> str:
        """Normalize collection name for Chroma requirements"""
        import re
        
        # Replace invalid characters
        normalized = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
        
        # Ensure starts and ends with alphanumeric
        if normalized and not normalized[0].isalnum():
            normalized = 'collection-' + normalized[1:]
        if normalized and not normalized[-1].isalnum():
            normalized = normalized[:-1]
        
        # Ensure length is 3-63 characters
        if len(normalized) < 3:
            normalized = f'collection-{normalized}'
        elif len(normalized) > 63:
            normalized = normalized[:63]
        
        return normalized
    
    async def create_namespace(self, namespace: str, dimension: int = 1536):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        
        try:
            self.client.create_collection(name=collection_name)
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                return True
            raise e
    
    async def delete_namespace(self, namespace: str):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception:
            return False
    
    async def upsert_vectors(self, namespace: str, vectors: List[Dict[str, Any]]):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        collection = self.client.get_or_create_collection(name=collection_name)
        
        # Format data for Chroma
        ids = [vector['id'] for vector in vectors]
        embeddings = [vector['values'] for vector in vectors]
        metadatas = [vector.get('metadata', {}) for vector in vectors]
        documents = [vector.get('metadata', {}).get('content', '') for vector in vectors]
        
        # Chroma upsert
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        return len(vectors)
    
    async def similarity_search(self, namespace: str, query_vector: List[float], 
                              top_k: int = 5, similarity_threshold: float = 0.7):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        
        try:
            collection = self.client.get_collection(name=collection_name)
            
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= similarity_threshold:
                        formatted_results.append({
                            'id': doc_id,
                            'score': similarity,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'content': results['documents'][0][i] if results['documents'] else ''
                        })
            
            return formatted_results
        except Exception as e:
            return []
    
    async def delete_vectors(self, namespace: str, vector_ids: List[str]):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=vector_ids)
            return True
        except Exception:
            return False
    
    async def get_namespace_stats(self, namespace: str):
        if not self.client:
            await self.connect()
        
        collection_name = self._normalize_collection_name(namespace)
        
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            return {
                'vector_count': count,
                'dimension': 1536  # Chroma doesn't expose dimension directly
            }
        except Exception:
            return {'vector_count': 0, 'dimension': 0}

# 3. vector_factory.py - Vector provider factory
class VectorProviderFactory:
    @staticmethod
    def create_provider(provider_name: str, config: Dict[str, Any]):
        """Create vector provider instance"""
        
        if provider_name == 'pinecone':
            return PineconeProvider(config)
        
        elif provider_name == 'chroma':
            return ChromaProvider(config)
        
        elif provider_name == 'qdrant':
            # Placeholder for Qdrant implementation
            # return QdrantProvider(config)
            raise NotImplementedError("Qdrant provider not implemented in this example")
        
        elif provider_name == 'lancedb':
            # Placeholder for LanceDB implementation
            # return LanceDBProvider(config)
            raise NotImplementedError("LanceDB provider not implemented in this example")
        
        else:
            raise ValueError(f"Unsupported vector provider: {provider_name}")

# 4. views.py - Vector database API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class VectorSearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            namespace = data.get('namespace')
            query_vector = data.get('query_vector', [])
            top_k = data.get('top_k', 5)
            similarity_threshold = data.get('similarity_threshold', 0.7)
            provider_name = data.get('provider')
            
            if not namespace or not query_vector:
                return JsonResponse({'error': 'Namespace and query_vector are required'}, status=400)
            
            # Get vector database configuration
            if provider_name:
                try:
                    db_config = VectorDatabase.objects.get(name=provider_name, is_active=True)
                except VectorDatabase.DoesNotExist:
                    return JsonResponse({'error': f'Provider {provider_name} not found'}, status=400)
            else:
                try:
                    db_config = VectorDatabase.objects.get(is_default=True, is_active=True)
                except VectorDatabase.DoesNotExist:
                    return JsonResponse({'error': 'No default vector database configured'}, status=400)
            
            # Create provider instance
            provider = VectorProviderFactory.create_provider(
                db_config.name, 
                db_config.connection_config
            )
            
            # Perform similarity search
            async def search():
                return await provider.similarity_search(
                    namespace, query_vector, top_k, similarity_threshold
                )
            
            results = asyncio.run(search())
            
            return JsonResponse({
                'success': True,
                'results': results,
                'provider': db_config.name,
                'namespace': namespace,
                'total_results': len(results)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class VectorUpsertView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            namespace = data.get('namespace')
            vectors = data.get('vectors', [])
            provider_name = data.get('provider')
            
            if not namespace or not vectors:
                return JsonResponse({'error': 'Namespace and vectors are required'}, status=400)
            
            # Get vector database configuration
            if provider_name:
                db_config = VectorDatabase.objects.get(name=provider_name, is_active=True)
            else:
                db_config = VectorDatabase.objects.get(is_default=True, is_active=True)
            
            # Create provider instance
            provider = VectorProviderFactory.create_provider(
                db_config.name, 
                db_config.connection_config
            )
            
            # Upsert vectors
            async def upsert():
                await provider.create_namespace(namespace, db_config.embedding_dimension)
                return await provider.upsert_vectors(namespace, vectors)
            
            count = asyncio.run(upsert())
            
            # Update namespace stats
            namespace_obj, created = VectorNamespace.objects.get_or_create(
                database=db_config,
                name=namespace,
                defaults={'vector_count': count}
            )
            if not created:
                namespace_obj.vector_count += count
                namespace_obj.save()
            
            return JsonResponse({
                'success': True,
                'vectors_upserted': count,
                'provider': db_config.name,
                'namespace': namespace
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class VectorNamespaceStatsView(View):
    def get(self, request, namespace):
        try:
            provider_name = request.GET.get('provider')
            
            # Get vector database configuration
            if provider_name:
                db_config = VectorDatabase.objects.get(name=provider_name, is_active=True)
            else:
                db_config = VectorDatabase.objects.get(is_default=True, is_active=True)
            
            # Create provider instance
            provider = VectorProviderFactory.create_provider(
                db_config.name, 
                db_config.connection_config
            )
            
            # Get stats from provider
            async def get_stats():
                return await provider.get_namespace_stats(namespace)
            
            stats = asyncio.run(get_stats())
            
            return JsonResponse({
                'namespace': namespace,
                'provider': db_config.name,
                'stats': stats
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class VectorProvidersView(View):
    def get(self, request):
        try:
            providers = []
            
            for db in VectorDatabase.objects.filter(is_active=True):
                namespaces = []
                for ns in db.namespaces.all():
                    namespaces.append({
                        'name': ns.name,
                        'vector_count': ns.vector_count,
                        'created_at': ns.created_at.isoformat()
                    })
                
                providers.append({
                    'name': db.name,
                    'display_name': db.display_name,
                    'is_default': db.is_default,
                    'embedding_dimension': db.embedding_dimension,
                    'distance_metric': db.distance_metric,
                    'namespaces': namespaces
                })
            
            return JsonResponse({'providers': providers})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import VectorSearchView, VectorUpsertView, VectorNamespaceStatsView, VectorProvidersView

urlpatterns = [
    path('vector/search/', VectorSearchView.as_view()),
    path('vector/upsert/', VectorUpsertView.as_view()),
    path('vector/namespace/<str:namespace>/stats/', VectorNamespaceStatsView.as_view()),
    path('vector/providers/', VectorProvidersView.as_view()),
]