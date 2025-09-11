# Feature: SQL Agent Capabilities
# Description: Specialized SQL agent tools for database querying with safety measures
# Library: Django, psycopg2, pymysql, pyodbc, sqlparse

# 1. models.py - SQL connection and query tracking
from django.db import models
import uuid
import json

class DatabaseConnection(models.Model):
    ENGINE_CHOICES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
        ('mssql', 'Microsoft SQL Server'),
        ('oracle', 'Oracle'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    database_id = models.CharField(max_length=100, unique=True)  # User-friendly identifier
    display_name = models.CharField(max_length=200)
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES)
    host = models.CharField(max_length=200)
    port = models.IntegerField()
    database_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=500)  # Encrypted in production
    connection_options = models.JSONField(default=dict)
    
    # Safety settings
    is_read_only = models.BooleanField(default=True)
    max_rows = models.IntegerField(default=1000)
    query_timeout_seconds = models.IntegerField(default=30)
    allowed_operations = models.JSONField(default=list)  # ['SELECT', 'SHOW', 'DESCRIBE']
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_tested = models.DateTimeField(null=True, blank=True)

class SQLQuery(models.Model):
    QUERY_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('blocked', 'Blocked by Safety'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    database = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE, related_name='queries')
    agent_name = models.CharField(max_length=100, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    raw_query = models.TextField()
    sanitized_query = models.TextField()
    query_type = models.CharField(max_length=20)  # SELECT, INSERT, UPDATE, etc.
    parameters = models.JSONField(default=dict)
    result_data = models.JSONField(null=True, blank=True)
    row_count = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=QUERY_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class DatabaseSchema(models.Model):
    database = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE, related_name='schema_info')
    table_name = models.CharField(max_length=200)
    column_name = models.CharField(max_length=200)
    data_type = models.CharField(max_length=100)
    is_nullable = models.BooleanField(default=True)
    is_primary_key = models.BooleanField(default=False)
    default_value = models.CharField(max_length=500, blank=True)
    column_comment = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('database', 'table_name', 'column_name')

# 2. sql_connectors.py - Database connection implementations
import psycopg2
import pymysql
import sqlite3
import time
import sqlparse
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseSQLConnector(ABC):
    def __init__(self, config):
        self.config = config
        self.database_id = config.get('database_id')
        self.is_read_only = config.get('is_read_only', True)
        self.max_rows = config.get('max_rows', 1000)
        self.query_timeout = config.get('query_timeout_seconds', 30)
        self.allowed_operations = config.get('allowed_operations', ['SELECT', 'SHOW', 'DESCRIBE'])
        self.connection = None
    
    @abstractmethod
    async def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute SQL query"""
        pass
    
    def validate_query_safety(self, query: str) -> Dict[str, Any]:
        """Validate query for safety (read-only, allowed operations)"""
        try:
            # Parse SQL query
            parsed = sqlparse.parse(query.strip())
            
            if not parsed:
                return {'valid': False, 'error': 'Could not parse SQL query'}
            
            # Get first statement
            statement = parsed[0]
            
            # Extract query type
            query_type = None
            for token in statement.flatten():
                if token.ttype in sqlparse.tokens.Keyword and token.value.upper() in [
                    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'SHOW', 'DESCRIBE'
                ]:
                    query_type = token.value.upper()
                    break
            
            if not query_type:
                return {'valid': False, 'error': 'Could not determine query type'}
            
            # Check if operation is allowed
            if query_type not in self.allowed_operations:
                return {
                    'valid': False, 
                    'error': f'Operation {query_type} not allowed. Allowed operations: {self.allowed_operations}'
                }
            
            # Additional safety checks for read-only mode
            if self.is_read_only and query_type in ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']:
                return {
                    'valid': False,
                    'error': f'Write operation {query_type} blocked in read-only mode'
                }
            
            # Check for LIMIT clause in SELECT statements
            if query_type == 'SELECT' and 'LIMIT' not in query.upper():
                # Automatically add LIMIT to prevent large result sets
                query = f"{query.rstrip(';')} LIMIT {self.max_rows}"
            
            return {
                'valid': True,
                'query_type': query_type,
                'sanitized_query': query
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Query validation failed: {str(e)}'}

class PostgreSQLConnector(BaseSQLConnector):
    async def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database_name'],
                user=self.config['username'],
                password=self.config['password'],
                connect_timeout=10
            )
            
            # Set read-only mode if configured
            if self.is_read_only:
                cursor = self.connection.cursor()
                cursor.execute("SET default_transaction_read_only = on;")
                self.connection.commit()
                cursor.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {str(e)}")
    
    async def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    async def execute_query(self, query: str) -> Dict[str, Any]:
        try:
            if not self.connection:
                await self.connect()
            
            cursor = self.connection.cursor()
            
            # Set query timeout
            cursor.execute(f"SET statement_timeout = {self.query_timeout * 1000};")
            
            start_time = time.time()
            cursor.execute(query)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Fetch results for SELECT queries
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                # Format results
                formatted_rows = []
                for row in rows:
                    formatted_rows.append(dict(zip(columns, row)))
                
                result = {
                    'rows': formatted_rows,
                    'columns': columns,
                    'count': len(formatted_rows),
                    'execution_time_ms': execution_time,
                    'error': None
                }
            else:
                # For non-SELECT queries
                self.connection.commit()
                result = {
                    'rows': [],
                    'columns': [],
                    'count': cursor.rowcount,
                    'execution_time_ms': execution_time,
                    'error': None
                }
            
            cursor.close()
            return result
            
        except Exception as e:
            return {
                'rows': [],
                'columns': [],
                'count': 0,
                'execution_time_ms': 0,
                'error': str(e)
            }

class MySQLConnector(BaseSQLConnector):
    async def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database_name'],
                connect_timeout=10,
                read_timeout=self.query_timeout,
                charset='utf8mb4'
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to connect to MySQL: {str(e)}")
    
    async def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    async def execute_query(self, query: str) -> Dict[str, Any]:
        try:
            if not self.connection:
                await self.connect()
            
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            start_time = time.time()
            cursor.execute(query)
            execution_time = int((time.time() - start_time) * 1000)
            
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                result = {
                    'rows': rows,
                    'columns': list(rows[0].keys()) if rows else [],
                    'count': len(rows),
                    'execution_time_ms': execution_time,
                    'error': None
                }
            else:
                self.connection.commit()
                result = {
                    'rows': [],
                    'columns': [],
                    'count': cursor.rowcount,
                    'execution_time_ms': execution_time,
                    'error': None
                }
            
            cursor.close()
            return result
            
        except Exception as e:
            return {
                'rows': [],
                'columns': [],
                'count': 0,
                'execution_time_ms': 0,
                'error': str(e)
            }

# 3. sql_agent_service.py - SQL agent service
class SQLAgentService:
    
    @staticmethod
    def get_database_connector(database_id: str):
        """Get database connector instance"""
        try:
            db_config = DatabaseConnection.objects.get(database_id=database_id, is_active=True)
            
            config = {
                'database_id': db_config.database_id,
                'host': db_config.host,
                'port': db_config.port,
                'database_name': db_config.database_name,
                'username': db_config.username,
                'password': db_config.password,  # In production, decrypt this
                'is_read_only': db_config.is_read_only,
                'max_rows': db_config.max_rows,
                'query_timeout_seconds': db_config.query_timeout_seconds,
                'allowed_operations': db_config.allowed_operations,
                **db_config.connection_options
            }
            
            if db_config.engine == 'postgresql':
                return PostgreSQLConnector(config)
            elif db_config.engine == 'mysql':
                return MySQLConnector(config)
            else:
                raise ValueError(f"Unsupported database engine: {db_config.engine}")
                
        except DatabaseConnection.DoesNotExist:
            raise ValueError(f"Database connection {database_id} not found")
    
    @staticmethod
    async def execute_safe_query(database_id: str, query: str, agent_name: str = None, 
                                session_id: str = None) -> Dict[str, Any]:
        """Execute SQL query with safety validations"""
        
        # Create query record
        try:
            db_config = DatabaseConnection.objects.get(database_id=database_id)
        except DatabaseConnection.DoesNotExist:
            return {'error': f'Database {database_id} not found'}
        
        sql_query = SQLQuery.objects.create(
            database=db_config,
            agent_name=agent_name or 'unknown',
            session_id=session_id,
            raw_query=query,
            status='pending'
        )
        
        start_time = time.time()
        
        try:
            # Get database connector
            connector = SQLAgentService.get_database_connector(database_id)
            
            # Validate query safety
            validation = connector.validate_query_safety(query)
            
            if not validation['valid']:
                sql_query.status = 'blocked'
                sql_query.error_message = validation['error']
                sql_query.save()
                
                return {
                    'success': False,
                    'error': validation['error'],
                    'query_blocked': True
                }
            
            # Update query record with sanitized query
            sql_query.sanitized_query = validation['sanitized_query']
            sql_query.query_type = validation['query_type']
            sql_query.status = 'running'
            sql_query.save()
            
            # Execute the query
            result = await connector.execute_query(validation['sanitized_query'])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update query record with results
            sql_query.result_data = result
            sql_query.row_count = result.get('count', 0)
            sql_query.execution_time_ms = execution_time
            sql_query.status = 'completed' if not result.get('error') else 'failed'
            sql_query.error_message = result.get('error', '')
            sql_query.completed_at = timezone.now()
            sql_query.save()
            
            # Disconnect
            await connector.disconnect()
            
            if result.get('error'):
                return {
                    'success': False,
                    'error': result['error'],
                    'execution_time_ms': execution_time
                }
            
            return {
                'success': True,
                'database_id': database_id,
                'query_type': validation['query_type'],
                'rows': result['rows'],
                'columns': result.get('columns', []),
                'row_count': result['count'],
                'execution_time_ms': execution_time,
                'query_id': str(sql_query.id)
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            sql_query.status = 'failed'
            sql_query.error_message = str(e)
            sql_query.execution_time_ms = execution_time
            sql_query.completed_at = timezone.now()
            sql_query.save()
            
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': execution_time
            }
    
    @staticmethod
    async def list_databases() -> List[Dict[str, Any]]:
        """List all available database connections"""
        databases = []
        
        for db in DatabaseConnection.objects.filter(is_active=True):
            databases.append({
                'database_id': db.database_id,
                'display_name': db.display_name,
                'engine': db.engine,
                'host': db.host,
                'database_name': db.database_name,
                'is_read_only': db.is_read_only,
                'max_rows': db.max_rows,
                'allowed_operations': db.allowed_operations
            })
        
        return databases
    
    @staticmethod
    async def list_tables(database_id: str) -> Dict[str, Any]:
        """List tables in a database"""
        try:
            connector = SQLAgentService.get_database_connector(database_id)
            
            # Get table list query based on database engine
            db_config = DatabaseConnection.objects.get(database_id=database_id)
            
            if db_config.engine == 'postgresql':
                table_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            elif db_config.engine == 'mysql':
                table_query = "SHOW TABLES"
            else:
                return {'error': f'Table listing not implemented for {db_config.engine}'}
            
            result = await connector.execute_query(table_query)
            await connector.disconnect()
            
            if result.get('error'):
                return {'error': result['error']}
            
            # Format table list
            tables = []
            for row in result['rows']:
                table_name = list(row.values())[0] if isinstance(row, dict) else row[0]
                tables.append(table_name)
            
            return {
                'success': True,
                'database_id': database_id,
                'tables': tables,
                'table_count': len(tables)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    async def get_table_schema(database_id: str, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table"""
        try:
            connector = SQLAgentService.get_database_connector(database_id)
            db_config = DatabaseConnection.objects.get(database_id=database_id)
            
            # Get schema query based on database engine
            if db_config.engine == 'postgresql':
                schema_query = f"""
                SELECT column_name, data_type, is_nullable, column_default, 
                       (SELECT COUNT(*) FROM information_schema.key_column_usage 
                        WHERE table_name = '{table_name}' AND column_name = columns.column_name) as is_primary_key
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND table_schema = 'public'
                ORDER BY ordinal_position
                """
            elif db_config.engine == 'mysql':
                schema_query = f"DESCRIBE {table_name}"
            else:
                return {'error': f'Schema inspection not implemented for {db_config.engine}'}
            
            result = await connector.execute_query(schema_query)
            await connector.disconnect()
            
            if result.get('error'):
                return {'error': result['error']}
            
            return {
                'success': True,
                'database_id': database_id,
                'table_name': table_name,
                'columns': result['rows'],
                'column_count': len(result['rows'])
            }
            
        except Exception as e:
            return {'error': str(e)}

# 4. views.py - SQL agent API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class SQLQueryView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            database_id = data.get('database_id')
            sql_query = data.get('sql_query')
            agent_name = data.get('agent_name', 'sql-agent')
            session_id = data.get('session_id')
            
            if not database_id or not sql_query:
                return JsonResponse({'error': 'database_id and sql_query are required'}, status=400)
            
            # Execute query asynchronously
            async def execute():
                return await SQLAgentService.execute_safe_query(
                    database_id, sql_query, agent_name, session_id
                )
            
            result = asyncio.run(execute())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class SQLDatabasesView(View):
    def get(self, request):
        try:
            async def get_databases():
                return await SQLAgentService.list_databases()
            
            databases = asyncio.run(get_databases())
            
            return JsonResponse({
                'databases': databases,
                'total_databases': len(databases)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class SQLTablesView(View):
    def get(self, request, database_id):
        try:
            async def get_tables():
                return await SQLAgentService.list_tables(database_id)
            
            result = asyncio.run(get_tables())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class SQLTableSchemaView(View):
    def get(self, request, database_id, table_name):
        try:
            async def get_schema():
                return await SQLAgentService.get_table_schema(database_id, table_name)
            
            result = asyncio.run(get_schema())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import SQLQueryView, SQLDatabasesView, SQLTablesView, SQLTableSchemaView

urlpatterns = [
    path('sql/query/', SQLQueryView.as_view()),
    path('sql/databases/', SQLDatabasesView.as_view()),
    path('sql/databases/<str:database_id>/tables/', SQLTablesView.as_view()),
    path('sql/databases/<str:database_id>/tables/<str:table_name>/schema/', SQLTableSchemaView.as_view()),
]