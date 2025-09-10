import uuid
import json
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
    WorkspaceThreadCreateSerializer,
    WorkspaceThreadUpdateSerializer,
    WorkspaceThreadChatSerializer,
    WorkspaceThreadListResponseSerializer,
    WorkspaceThreadDetailResponseSerializer,
    ChatHistoryResponseSerializer,
    ChatResponseSerializer,
    ChatFeedbackSerializer,
    ChatUpdateSerializer,
    ChatDeleteSerializer,
    ChatDeleteEditedSerializer,
    ThreadForkSerializer,
    ThreadForkResponseSerializer,
    ChatHideSerializer,
    ChatHideResponseSerializer
)

logger = logging.getLogger(__name__)


class WorkspaceThreadViewSet:
    """ViewSet for workspace thread operations"""
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def create_thread(request, slug):
        """
        Create a new workspace thread
        POST /v1/workspace/:slug/thread/new
        """
        try:
            serializer = WorkspaceThreadCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            user_id = serializer.validated_data.get('userId')
            name = serializer.validated_data.get('name')
            thread_slug = serializer.validated_data.get('slug')
            
            # TODO: Integrate with actual Workspace.get() and WorkspaceThread.new() methods
            # workspace = await Workspace.get({ slug: wslug })
            # if not workspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # If the system is not multi-user and you pass in a userId
            # it needs to be nullified as no users exist
            # if not response.locals.multiUserMode and !!userId:
            #     userId = null
            
            # thread, message = await WorkspaceThread.new(
            #     workspace,
            #     userId ? Number(userId) : null,
            #     { name, slug }
            # )
            
            thread_data = {
                "id": 1,
                "name": name or "Thread",
                "slug": thread_slug or str(uuid.uuid4()),
                "user_id": user_id,
                "workspace_id": 1
            }
            
            return Response({
                "thread": thread_data,
                "message": None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating thread for workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def update_thread(request, slug, thread_slug):
        """
        Update thread name by its unique slug
        POST /v1/workspace/:slug/thread/:threadSlug/update
        """
        try:
            serializer = WorkspaceThreadUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            name = serializer.validated_data['name']
            
            # TODO: Integrate with actual Workspace.get() and WorkspaceThread methods
            # workspace = await Workspace.get({ slug })
            # thread = await WorkspaceThread.get({
            #     slug: threadSlug,
            #     workspace_id: workspace.id
            # })
            
            # if not workspace or not thread:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # thread, message = await WorkspaceThread.update(thread, { name })
            
            thread_data = {
                "id": 1,
                "name": name,
                "slug": thread_slug,
                "user_id": 1,
                "workspace_id": 1
            }
            
            return Response({
                "thread": thread_data,
                "message": None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating thread {thread_slug} in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete_thread(request, slug, thread_slug):
        """
        Delete a workspace thread
        DELETE /v1/workspace/:slug/thread/:threadSlug
        """
        try:
            # TODO: Integrate with actual Workspace.get() and WorkspaceThread.delete() methods
            # workspace = await Workspace.get({ slug })
            # if not workspace:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # await WorkspaceThread.delete({
            #     slug: threadSlug,
            #     workspace_id: workspace.id
            # })
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting thread {thread_slug} in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def get_thread_chats(request, slug, thread_slug):
        """
        Get chats for a workspace thread
        GET /v1/workspace/:slug/thread/:threadSlug/chats
        """
        try:
            # TODO: Integrate with actual Workspace.get() and WorkspaceThread.get() methods
            # workspace = await Workspace.get({ slug })
            # thread = await WorkspaceThread.get({
            #     slug: threadSlug,
            #     workspace_id: workspace.id
            # })
            
            # if not workspace or not thread:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # history = await WorkspaceChats.where(
            #     {
            #         workspaceId: workspace.id,
            #         thread_id: thread.id,
            #         api_session_id: null, // Do not include API session chats
            #         include: true
            #     },
            #     null,
            #     { id: "asc" }
            # )
            
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
            logger.error(f"Error getting thread chats for {thread_slug} in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def chat_with_thread(request, slug, thread_slug):
        """
        Chat with a workspace thread
        POST /v1/workspace/:slug/thread/:threadSlug/chat
        """
        try:
            serializer = WorkspaceThreadChatSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            message = serializer.validated_data['message']
            mode = serializer.validated_data.get('mode', 'query')
            user_id = serializer.validated_data.get('userId')
            attachments = serializer.validated_data.get('attachments', [])
            reset = serializer.validated_data.get('reset', False)
            
            # TODO: Integrate with actual Workspace.get() and WorkspaceThread.get() methods
            # workspace = await Workspace.get({ slug })
            # thread = await WorkspaceThread.get({
            #     slug: threadSlug,
            #     workspace_id: workspace.id
            # })
            
            # if not workspace or not thread:
            #     return Response({
            #         "id": str(uuid.uuid4()),
            #         "type": "abort",
            #         "textResponse": None,
            #         "sources": [],
            #         "close": True,
            #         "error": f"Workspace {slug} or thread {threadSlug} is not valid."
            #     }, status=status.HTTP_400_BAD_REQUEST)
            
            # user = userId ? await User.get({ id: Number(userId) }) : null
            # result = await ApiChatHandler.chatSync({
            #     workspace, message, mode, user, thread, attachments, reset
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
            logger.error(f"Error in thread chat for {thread_slug} in workspace {slug}: {e}")
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
    def stream_chat_with_thread(request, slug, thread_slug):
        """
        Stream chat with a workspace thread
        POST /v1/workspace/:slug/thread/:threadSlug/stream-chat
        """
        try:
            serializer = WorkspaceThreadChatSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            message = serializer.validated_data['message']
            mode = serializer.validated_data.get('mode', 'query')
            user_id = serializer.validated_data.get('userId')
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
            logger.error(f"Error in thread stream chat for {thread_slug} in workspace {slug}: {e}")
            return Response({
                "id": str(uuid.uuid4()),
                "type": "abort",
                "textResponse": None,
                "sources": [],
                "close": True,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatManagementViewSet:
    """ViewSet for chat management operations"""
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def update_chat(request, slug):
        """
        Update chat content
        POST /v1/workspace/:slug/update-chat
        """
        try:
            serializer = ChatUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            chat_id = serializer.validated_data['chatId']
            new_text = serializer.validated_data['newText']
            
            if not new_text or not str(new_text).strip():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: Integrate with actual WorkspaceChats methods
            # existingChat = await WorkspaceChats.get({
            #     workspaceId: workspace.id,
            #     thread_id: null,
            #     user_id: user?.id,
            #     id: Number(chatId)
            # })
            # if not existingChat:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # chatResponse = safeJsonParse(existingChat.response, null)
            # if not chatResponse:
            #     return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # await WorkspaceChats._update(existingChat.id, {
            #     response: JSON.stringify({
            #         ...chatResponse,
            #         text: String(newText)
            #     })
            # })
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating chat in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def chat_feedback(request, slug, chat_id):
        """
        Update chat feedback
        POST /v1/workspace/:slug/chat-feedback/:chatId
        """
        try:
            serializer = ChatFeedbackSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            feedback = serializer.validated_data.get('feedback')
            
            # TODO: Integrate with actual WorkspaceChats methods
            # existingChat = await WorkspaceChats.get({
            #     id: Number(chatId),
            #     workspaceId: response.locals.workspace.id
            # })
            
            # if not existingChat:
            #     return Response(status=status.HTTP_404_NOT_FOUND)
            
            # result = await WorkspaceChats.updateFeedbackScore(chatId, feedback)
            
            return Response({"success": True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating chat feedback for {chat_id} in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete_chats(request, slug):
        """
        Delete specific chats
        DELETE /v1/workspace/:slug/delete-chats
        """
        try:
            serializer = ChatDeleteSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            chat_ids = serializer.validated_data.get('chatIds', [])
            
            if not isinstance(chat_ids, list):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: Integrate with actual WorkspaceChats.delete() method
            # await WorkspaceChats.delete({
            #     id: { in: chatIds.map((id) => Number(id)) },
            #     user_id: user?.id ?? null,
            #     workspaceId: workspace.id
            # })
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting chats in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete_edited_chats(request, slug):
        """
        Delete edited chats from a starting point
        DELETE /v1/workspace/:slug/delete-edited-chats
        """
        try:
            serializer = ChatDeleteEditedSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            starting_id = serializer.validated_data['startingId']
            
            # TODO: Integrate with actual WorkspaceChats.delete() method
            # await WorkspaceChats.delete({
            #     workspaceId: workspace.id,
            #     thread_id: null,
            #     user_id: user?.id,
            #     id: { gte: Number(startingId) }
            # })
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting edited chats in workspace {slug}: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def fork_thread(request, slug):
        """
        Fork a thread from a specific chat point
        POST /v1/workspace/:slug/thread/fork
        """
        try:
            serializer = ThreadForkSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            chat_id = serializer.validated_data['chatId']
            thread_slug = serializer.validated_data.get('threadSlug')
            
            if not chat_id:
                return Response({"message": "chatId is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: Integrate with actual WorkspaceThread and WorkspaceChats methods
            # Get threadId we are branching from if that request body is sent
            # and is a valid thread slug
            # threadId = !!threadSlug ? 
            #     (await WorkspaceThread.get({
            #         slug: String(threadSlug),
            #         workspace_id: workspace.id
            #     }))?.id ?? null : null
            
            # chatsToFork = await WorkspaceChats.where({
            #     workspaceId: workspace.id,
            #     user_id: user?.id,
            #     include: true, // only duplicate visible chats
            #     thread_id: threadId,
            #     api_session_id: null, // Do not include API session chats
            #     id: { lte: Number(chatId) }
            # }, null, { id: "asc" })
            
            # newThread, threadError = await WorkspaceThread.new(workspace, user?.id)
            # if threadError:
            #     return Response({"error": threadError}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # await WorkspaceChats.bulkCreate(chatsData)
            # await WorkspaceThread.update(newThread, {
            #     name: !!lastMessageText ? truncate(lastMessageText, 22) : "Forked Thread"
            # })
            
            new_thread_slug = str(uuid.uuid4())
            
            return Response({"newThreadSlug": new_thread_slug}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error forking thread in workspace {slug}: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    @api_view(['PUT'])
    @permission_classes([IsAuthenticated])
    def hide_chat(request, chat_id):
        """
        Hide a chat by setting include to false
        PUT /v1/workspace/workspace-chats/:id
        """
        try:
            # TODO: Integrate with actual WorkspaceChats methods
            # validChat = await WorkspaceChats.get({
            #     id: Number(id),
            #     user_id: user?.id ?? null
            # })
            # if not validChat:
            #     return Response({"success": False, "error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # await WorkspaceChats._update(validChat.id, { include: false })
            
            return Response({"success": True, "error": None}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error hiding chat {chat_id}: {e}")
            return Response({"success": False, "error": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)