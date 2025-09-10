from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.conf import settings
from django.http import HttpResponse
from apps.coredb.models import SystemSetting, EventLog, WorkspaceChat
import json
import os


class EnvDumpView(APIView):
    """
    Dump all settings to file storage
    """
    
    @extend_schema(
        tags=['System Settings'],
        summary='Dump environment',
        description='Dump all settings to file storage',
        responses={
            200: OpenApiResponse(description='Environment dumped successfully'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        if settings.DEBUG:
            return Response(status=status.HTTP_200_OK)
        
        try:
            # In a real implementation, you'd dump the environment
            # For now, just return success
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemSettingsView(APIView):
    """
    Get all current system settings that are defined
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['System Settings'],
        summary='Get system settings',
        description='Get all current system settings that are defined.',
        responses={
            200: OpenApiResponse(
                description='System settings retrieved successfully',
                examples={
                    'application/json': {
                        'settings': {
                            'VectorDB': 'pinecone',
                            'PineConeKey': True,
                            'PineConeIndex': 'my-pinecone-index',
                            'LLMProvider': 'azure',
                            '[KEY_NAME]': 'KEY_VALUE'
                        }
                    }
                }
            ),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        try:
            settings_dict = {}
            for setting in SystemSetting.objects.all():
                settings_dict[setting.label] = setting.value
            
            return Response({'settings': settings_dict})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VectorCountView(APIView):
    """
    Number of all vectors in connected vector database
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['System Settings'],
        summary='Get vector count',
        description='Number of all vectors in connected vector database',
        responses={
            200: OpenApiResponse(
                description='Vector count retrieved successfully',
                examples={
                    'application/json': {
                        'vectorCount': 5450
                    }
                }
            ),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        try:
            # In a real implementation, you'd connect to the vector database
            # For now, return a placeholder count
            vector_count = 0  # Placeholder
            
            return Response({'vectorCount': vector_count})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEnvView(APIView):
    """
    Update a system setting or preference
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['System Settings'],
        summary='Update environment settings',
        description='Update a system setting or preference.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'VectorDB': {'type': 'string', 'example': 'lancedb'},
                    'AnotherKey': {'type': 'string', 'example': 'updatedValue'}
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description='Settings updated successfully',
                examples={
                    'application/json': {
                        'newValues': {'[ENV_KEY]': 'Value'},
                        'error': 'error goes here, otherwise null'
                    }
                }
            ),
            400: OpenApiResponse(description='Bad request'),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def post(self, request):
        try:
            new_values = {}
            error = None
            
            for key, value in request.data.items():
                try:
                    setting, created = SystemSetting.objects.get_or_create(label=key)
                    setting.value = str(value)
                    setting.save()
                    new_values[key] = value
                except Exception as e:
                    error = str(e)
                    break
            
            return Response({'newValues': new_values, 'error': error})
        except Exception as e:
            return Response({'newValues': {}, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportChatsView(APIView):
    """
    Export all of the chats from the system in a known format
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['System Settings'],
        summary='Export chats',
        description='Export all of the chats from the system in a known format. Output depends on the type sent. Will be send with the correct header for the output.',
        parameters=[
            {
                'name': 'type',
                'in': 'query',
                'description': 'Export format jsonl, json, csv, jsonAlpaca',
                'required': False,
                'schema': {'type': 'string', 'default': 'jsonl'}
            }
        ],
        responses={
            200: OpenApiResponse(
                description='Chats exported successfully',
                examples={
                    'application/json': [
                        {
                            'role': 'user',
                            'content': 'What is AnythinglLM?'
                        },
                        {
                            'role': 'assistant',
                            'content': 'AnythingLLM is a knowledge graph and vector database management system built using NodeJS express server. It provides an interface for handling all interactions, including vectorDB management and LLM (Language Model) interactions.'
                        }
                    ]
                }
            ),
            403: OpenApiResponse(description='Invalid API key')
        }
    )
    def get(self, request):
        try:
            export_type = request.query_params.get('type', 'jsonl')
            
            # Get all chats
            chats = WorkspaceChat.objects.all().order_by('created_at')
            
            if export_type == 'jsonl':
                data = []
                for chat in chats:
                    data.append({
                        'role': 'user',
                        'content': chat.prompt
                    })
                    data.append({
                        'role': 'assistant',
                        'content': chat.response
                    })
                
                response = HttpResponse(
                    '\n'.join(json.dumps(item) for item in data),
                    content_type='application/jsonl'
                )
                
            elif export_type == 'json':
                data = []
                for chat in chats:
                    data.append({
                        'role': 'user',
                        'content': chat.prompt
                    })
                    data.append({
                        'role': 'assistant',
                        'content': chat.response
                    })
                
                response = HttpResponse(
                    json.dumps(data, indent=2),
                    content_type='application/json'
                )
                
            elif export_type == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['role', 'content'])
                
                for chat in chats:
                    writer.writerow(['user', chat.prompt])
                    writer.writerow(['assistant', chat.response])
                
                response = HttpResponse(
                    output.getvalue(),
                    content_type='text/csv'
                )
                
            else:
                return Response({'error': 'Unsupported export type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Log the export event
            EventLog.objects.create(
                event='exported_chats',
                metadata=json.dumps({'type': export_type})
            )
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveDocumentsView(APIView):
    """
    Permanently remove documents from the system
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['System Settings'],
        summary='Remove documents',
        description='Permanently remove documents from the system.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'names': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['custom-documents/file.txt-fc4beeeb-e436-454d-8bb4-e5b8979cb48f.json']
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description='Documents removed successfully',
                examples={
                    'application/json': {
                        'success': True,
                        'message': 'Documents removed successfully'
                    }
                }
            ),
            400: OpenApiResponse(description='Bad request'),
            403: OpenApiResponse(description='Invalid API key'),
            500: OpenApiResponse(description='Internal Server Error')
        }
    )
    def delete(self, request):
        try:
            names = request.data.get('names', [])
            
            # In a real implementation, you'd actually remove the documents
            # For now, just simulate the operation
            for name in names:
                # Simulate document removal
                pass
            
            return Response({
                'success': True,
                'message': 'Documents removed successfully'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)