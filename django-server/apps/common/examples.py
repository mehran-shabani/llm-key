"""
Example Django views using common utilities.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from apps.common.http import get_request_body, create_error_response, create_success_response
from apps.common.validation import validate_required_fields, validate_email
from apps.common.errors import ValidationError, NotFoundError
from apps.common.pagination import paginate_queryset, get_pagination_params
from apps.common.logger import log_info, log_error
from apps.common.file_utils import sanitize_filename, validate_file_size


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    """Example view for creating a user with validation."""
    try:
        data = get_request_body(request)
        
        # Validate required fields
        validation_result = validate_required_fields(data, ["name", "email", "password"])
        if not validation_result['valid']:
            return create_error_response(
                "Validation failed",
                400,
                {"missing_fields": validation_result['missing_fields']}
            )
        
        # Validate email format
        if not validate_email(data['email']):
            raise ValidationError("Invalid email format", field="email")
        
        # Log user creation
        log_info(f"Creating user: {data['email']}")
        
        # Here you would create the user in the database
        # user = User.objects.create(**data)
        
        return create_success_response(
            {"user_id": 123, "email": data['email']},
            "User created successfully"
        )
        
    except ValidationError as e:
        log_error(f"Validation error: {e.message}")
        return create_error_response(e.message, e.status_code, e.details)
    except Exception as e:
        log_error(f"Unexpected error creating user: {str(e)}")
        return create_error_response("Internal server error", 500)


@require_http_methods(["GET"])
def list_users(request):
    """Example view for listing users with pagination."""
    try:
        # Get pagination parameters
        page, page_size = get_pagination_params(request)
        
        # Mock queryset (replace with actual User queryset)
        users = [
            {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(1, 101)
        ]
        
        # Paginate results
        result = paginate_queryset(users, page, page_size)
        
        log_info(f"Listed users: page {page}, size {page_size}")
        
        return JsonResponse(result)
        
    except Exception as e:
        log_error(f"Error listing users: {str(e)}")
        return create_error_response("Internal server error", 500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Example view for file upload with validation."""
    try:
        if 'file' not in request.FILES:
            return create_error_response("No file provided", 400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file size (e.g., 10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if not validate_file_size(uploaded_file.size, max_size):
            return create_error_response("File too large", 400)
        
        # Sanitize filename
        safe_filename = sanitize_filename(uploaded_file.name)
        
        log_info(f"Uploading file: {safe_filename}, size: {uploaded_file.size}")
        
        # Here you would save the file
        # with default_storage.open(safe_filename, 'wb') as destination:
        #     for chunk in uploaded_file.chunks():
        #         destination.write(chunk)
        
        return create_success_response(
            {"filename": safe_filename, "size": uploaded_file.size},
            "File uploaded successfully"
        )
        
    except Exception as e:
        log_error(f"Error uploading file: {str(e)}")
        return create_error_response("Internal server error", 500)


class UserAPIView(View):
    """Example class-based view using common utilities."""
    
    def get(self, request, user_id):
        """Get user by ID."""
        try:
            # Mock user lookup
            if user_id == "999":
                raise NotFoundError("User not found")
            
            user_data = {
                "id": user_id,
                "name": f"User {user_id}",
                "email": f"user{user_id}@example.com"
            }
            
            log_info(f"Retrieved user: {user_id}")
            return create_success_response(user_data)
            
        except NotFoundError as e:
            return create_error_response(e.message, e.status_code)
        except Exception as e:
            log_error(f"Error retrieving user {user_id}: {str(e)}")
            return create_error_response("Internal server error", 500)
    
    def put(self, request, user_id):
        """Update user."""
        try:
            data = get_request_body(request)
            
            # Validate required fields for update
            validation_result = validate_required_fields(data, ["name"])
            if not validation_result['valid']:
                return create_error_response(
                    "Validation failed",
                    400,
                    {"missing_fields": validation_result['missing_fields']}
                )
            
            # Mock user update
            updated_user = {
                "id": user_id,
                "name": data["name"],
                "email": f"user{user_id}@example.com"
            }
            
            log_info(f"Updated user: {user_id}")
            return create_success_response(updated_user, "User updated successfully")
            
        except Exception as e:
            log_error(f"Error updating user {user_id}: {str(e)}")
            return create_error_response("Internal server error", 500)