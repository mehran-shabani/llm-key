import uuid
import logging
from typing import Dict, Any, List, Optional
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    WorkspaceCreateSerializer,
    WorkspaceUpdateSerializer,
    WorkspaceEmbeddingsUpdateSerializer,
    WorkspacePinUpdateSerializer,
    WorkspaceChatSerializer,
    WorkspaceVectorSearchSerializer,
    WorkspaceChatHistorySerializer,
    WorkspaceListResponseSerializer,
    WorkspaceDetailResponseSerializer,
    ChatHistoryResponseSerializer,
    ChatResponseSerializer,
    VectorSearchResponseSerializer
)

logger = logging.getLogger(__name__)


class WorkspaceViewSet:
    """ViewSet for workspace operations"""
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def create_workspace(request):
        """
        Create a new workspace
        POST /v1/workspace/new
        """
        try:
            serializer = WorkspaceCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"workspace": None, "message": "Invalid data"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract validated data
            validated_data = serializer.validated_data
            name = validated_data.get('name')
            
            # Create workspace using coredb models
            # This would integrate with the existing Workspace model
            workspace_data = {
                "id": 79,  # This would come from actual database
                "name": name or "Sample workspace",
                "slug": f"sample-workspace-{uuid.uuid4().hex[:8]}",
                "createdAt": "2023-08-17 00:45:03",
                "lastUpdatedAt": "2023-08-17 00:45:03",
                "openAiTemp": validated_data.get('openAiTemp'),
                "openAiHistory": validated_data.get('openAiHistory', 20),
                "openAiPrompt": validated_data.get('openAiPrompt'),
                "similarityThreshold": validated_data.get('similarityThreshold'),
                "topN": validated_data.get('topN'),
                "chatMode": validated_data.get('chatMode'),
            }
            
            # TODO: Integrate with actual Workspace.new() method
            # workspace, message = await Workspace.new(name, None, additionalFields)
            
            return Response({
                "workspace": workspace_data,
                "message": "Workspace created"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            return Response(
                {"workspace": None, "message": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def list_workspaces(request):
        """
        List all current workspaces
        GET /v1/workspaces
        """
        try:
            # TODO: Integrate with actual Workspace._findMany() method
            workspaces_data = [
                {
                    "id": 79,
                    "name": "Sample workspace",
                    "slug": "sample-workspace",
                    "createdAt": "2023-08-17 00:45:03",
                    "openAiTemp": None,
                    "lastUpdatedAt": "2023-08-17 00:45:03",
                    "openAiHistory": 20,
                    "openAiPrompt": None,
                    "threads": []
                }
            ]
            
            return Response({"workspaces": workspaces_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing workspaces: {e}")
            return Response(
                {"workspaces": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def get_workspace(request, slug):
        """
        Get a workspace by its unique slug
        GET /v1/workspace/:slug
        """
        try:
            # TODO: Integrate with actual Workspace._findMany() method
            workspace_data = [
                {
                    "id": 79,
                    "name": "My workspace",
                    "slug": slug,
                    "createdAt": "2023-08-17 00:45:03",
                    "openAiTemp": None,
                    "lastUpdatedAt": "2023-08-17 00:45:03",
                    "openAiHistory": 20,
                    "openAiPrompt": None,
                    "documents": [],
                    "threads": []
                }
            ]
            
            return Response({"workspace": workspace_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting workspace {slug}: {e}")
            return Response(
                {"workspace": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete_workspace(request, slug):
        """
        Delete a workspace by its slug
        DELETE /v1/workspace/:slug
        """
        try:
            # TODO: Integrate with actual Workspace.get() and deletion methods
            # workspace = await Workspace.get({ slug })
            # if not workspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # await WorkspaceChats.delete({ workspaceId: workspaceId })
            # await DocumentVectors.deleteForWorkspace(workspaceId)
            # await Document.delete({ workspaceId: workspaceId })
            # await Workspace.delete({ id: workspaceId })
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def update_workspace(request, slug):
        """
        Update workspace settings by its unique slug
        POST /v1/workspace/:slug/update
        """
        try:
            serializer = WorkspaceUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: Integrate with actual Workspace.get() and update methods
            # currWorkspace = await Workspace.get({ slug })
            # if not currWorkspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # workspace, message = await Workspace.update(currWorkspace.id, data)
            
            workspace_data = {
                "id": 79,
                "name": "My workspace",
                "slug": slug,
                "createdAt": "2023-08-17 00:45:03",
                "openAiTemp": None,
                "lastUpdatedAt": "2023-08-17 00:45:03",
                "openAiHistory": 20,
                "openAiPrompt": None,
                "documents": []
            }
            
            return Response({
                "workspace": workspace_data,
                "message": None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def get_workspace_chats(request, slug):
        """
        Get a workspace's chats regardless of user by its unique slug
        GET /v1/workspace/:slug/chats
        """
        try:
            api_session_id = request.GET.get('apiSessionId')
            limit = int(request.GET.get('limit', 100))
            order_by = request.GET.get('orderBy', 'asc')
            
            # Validate parameters
            valid_limit = max(1, limit)
            valid_order_by = order_by if order_by in ['asc', 'desc'] else 'asc'
            
            # TODO: Integrate with actual Workspace.get() and WorkspaceChats methods
            # workspace = await Workspace.get({ slug })
            # if not workspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # history = api_session_id ? 
            #     await WorkspaceChats.forWorkspaceByApiSessionId(workspace.id, api_session_id, valid_limit, { createdAt: valid_order_by }) :
            #     await WorkspaceChats.forWorkspace(workspace.id, valid_limit, { createdAt: valid_order_by })
            
            history_data = [
                {
                    "role": "user",
                    "content": "What is AnythingLLM?",
                    "sentAt": 1692851630
                },
                {
                    "role": "assistant",
                    "content": "AnythingLLM is a platform that allows you to convert notes, PDFs, and other source materials into a chatbot...",
                    "sources": [{"source": "object about source document and snippets used"}]
                }
            ]
            
            return Response({"history": history_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting workspace chats for {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def update_embeddings(request, slug):
        """
        Add or remove documents from a workspace by its unique slug
        POST /v1/workspace/:slug/update-embeddings
        """
        try:
            serializer = WorkspaceEmbeddingsUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            adds = serializer.validated_data.get('adds', [])
            deletes = serializer.validated_data.get('deletes', [])
            
            # TODO: Integrate with actual Workspace.get() and Document methods
            # currWorkspace = await Workspace.get({ slug })
            # if not currWorkspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # await Document.removeDocuments(currWorkspace, deletes)
            # await Document.addDocuments(currWorkspace, adds)
            # updatedWorkspace = await Workspace.get({ id: Number(currWorkspace.id) })
            
            workspace_data = {
                "id": 79,
                "name": "My workspace",
                "slug": slug,
                "createdAt": "2023-08-17 00:45:03",
                "openAiTemp": None,
                "lastUpdatedAt": "2023-08-17 00:45:03",
                "openAiHistory": 20,
                "openAiPrompt": None,
                "documents": []
            }
            
            return Response({"workspace": workspace_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating embeddings for workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def update_pin(request, slug):
        """
        Add or remove pin from a document in a workspace by its unique slug
        POST /v1/workspace/:slug/update-pin
        """
        try:
            serializer = WorkspacePinUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            doc_path = serializer.validated_data['docPath']
            pin_status = serializer.validated_data.get('pinStatus', False)
            
            # TODO: Integrate with actual Workspace.get() and Document methods
            # workspace = await Workspace.get({ slug })
            # document = await Document.get({ workspaceId: workspace.id, docpath: docPath })
            # if not document:
            #     return Response(status=status.HTTP_404_NOT_FOUND)
            
            # await Document.update(document.id, { pinned: pinStatus })
            
            return Response(
                {"message": "Pin status updated successfully"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error updating pin status for workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def chat(request, slug):
        """
        Execute a chat with a workspace
        POST /v1/workspace/:slug/chat
        """
        try:
            serializer = WorkspaceChatSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            message = serializer.validated_data['message']
            mode = serializer.validated_data.get('mode', 'query')
            session_id = serializer.validated_data.get('sessionId')
            attachments = serializer.validated_data.get('attachments', [])
            reset = serializer.validated_data.get('reset', False)
            
            # TODO: Integrate with actual Workspace.get() and ApiChatHandler
            # workspace = await Workspace.get({ slug: String(slug) })
            # if not workspace:
            #     return Response({
            #         "id": str(uuid.uuid4()),
            #         "type": "abort",
            #         "textResponse": None,
            #         "sources": [],
            #         "close": True,
            #         "error": f"Workspace {slug} is not a valid workspace."
            #     }, status=status.HTTP_400_BAD_REQUEST)
            
            # result = await ApiChatHandler.chatSync({
            #     workspace, message, mode, user: null, thread: null,
            #     sessionId: !!sessionId ? String(sessionId) : null,
            #     attachments, reset
            # })
            
            result = {
                "id": str(uuid.uuid4()),
                "type": "textResponse",
                "textResponse": "Response to your query",
                "sources": [{"title": "anythingllm.txt", "chunk": "This is a context chunk used in the answer of the prompt by the LLM."}],
                "close": True,
                "error": None
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in workspace chat for {slug}: {e}")
            return Response({
                "id": str(uuid.uuid4()),
                "type": "abort",
                "textResponse": None,
                "sources": [],
                "close": True,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def stream_chat(request, slug):
        """
        Execute a streamable chat with a workspace
        POST /v1/workspace/:slug/stream-chat
        """
        try:
            serializer = WorkspaceChatSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            message = serializer.validated_data['message']
            mode = serializer.validated_data.get('mode', 'query')
            session_id = serializer.validated_data.get('sessionId')
            attachments = serializer.validated_data.get('attachments', [])
            reset = serializer.validated_data.get('reset', False)
            
            # TODO: Integrate with actual streaming chat implementation
            # This would use Django's StreamingHttpResponse for SSE
            
            def event_stream():
                yield f"data: {json.dumps({'id': str(uuid.uuid4()), 'type': 'textResponseChunk', 'textResponse': 'First chunk', 'sources': [], 'close': False, 'error': None})}\n\n"
                yield f"data: {json.dumps({'id': str(uuid.uuid4()), 'type': 'textResponseChunk', 'textResponse': 'chunk two', 'sources': [], 'close': False, 'error': None})}\n\n"
                yield f"data: {json.dumps({'id': str(uuid.uuid4()), 'type': 'textResponseChunk', 'textResponse': 'final chunk of LLM output!', 'sources': [{'title': 'anythingllm.txt', 'chunk': 'This is a context chunk used in the answer of the prompt by the LLM.'}], 'close': True, 'error': None})}\n\n"
            
            response = StreamingHttpResponse(
                event_stream(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            response['Connection'] = 'keep-alive'
            
            return response
            
        except Exception as e:
            logger.error(f"Error in workspace stream chat for {slug}: {e}")
            return Response({
                "id": str(uuid.uuid4()),
                "type": "abort",
                "textResponse": None,
                "sources": [],
                "close": True,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def vector_search(request, slug):
        """
        Perform a vector similarity search in a workspace
        POST /v1/workspace/:slug/vector-search
        """
        try:
            serializer = WorkspaceVectorSearchSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            query = serializer.validated_data['query']
            top_n = serializer.validated_data.get('topN')
            score_threshold = serializer.validated_data.get('scoreThreshold')
            
            # TODO: Integrate with actual Workspace.get() and VectorDb methods
            # workspace = await Workspace.get({ slug: String(slug) })
            # if not workspace:
            #     return Response({"message": f"Workspace {slug} is not a valid workspace."}, status=status.HTTP_400_BAD_REQUEST)
            
            # VectorDb = getVectorDbClass()
            # hasVectorizedSpace = await VectorDb.hasNamespace(workspace.slug)
            # embeddingsCount = await VectorDb.namespaceCount(workspace.slug)
            
            # if not hasVectorizedSpace or embeddingsCount === 0:
            #     return Response({"results": [], "message": "No embeddings found for this workspace."}, status=status.HTTP_200_OK)
            
            # results = await VectorDb.performSimilaritySearch({
            #     namespace: workspace.slug,
            #     input: String(query),
            #     LLMConnector: getLLMProvider(),
            #     similarityThreshold: parseSimilarityThreshold(),
            #     topN: parseTopN(),
            #     rerank: workspace?.vectorSearchMode === "rerank"
            # })
            
            results_data = [
                {
                    "id": "5a6bee0a-306c-47fc-942b-8ab9bf3899c4",
                    "text": "Document chunk content...",
                    "metadata": {
                        "url": "file://document.txt",
                        "title": "document.txt",
                        "author": "no author specified",
                        "description": "no description found",
                        "docSource": "post:123456",
                        "chunkSource": "document.txt",
                        "published": "12/1/2024, 11:39:39 AM",
                        "wordCount": 8,
                        "tokenCount": 9
                    },
                    "distance": 0.541887640953064,
                    "score": 0.45811235904693604
                }
            ]
            
            return Response({"results": results_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in vector search for workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)