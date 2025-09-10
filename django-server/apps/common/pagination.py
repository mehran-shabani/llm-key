"""
Pagination utilities for Django applications.
Contains pagination helpers and response formatters.
"""

from typing import Any, Dict, List, Optional, Tuple

from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import JsonResponse


def get_pagination_params(request: HttpRequest) -> Tuple[int, int]:
    """
    Extract pagination parameters from request.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        Tuple of (page_number, page_size)
    """
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Validate parameters
    page = max(1, page)
    page_size = max(1, min(page_size, 100))  # Limit max page size
    
    return page, page_size


def paginate_queryset(queryset: Any, page: int, page_size: int) -> Dict[str, Any]:
    """
    Paginate a Django queryset.
    
    Args:
        queryset: Django queryset to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary with pagination data
    """
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except Exception:
        # If page is out of range, return last page
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        'items': list(page_obj.object_list),
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
    }


def paginate_list(items: List[Any], page: int, page_size: int) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary with pagination data
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    # Calculate start and end indices
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Get items for current page
    page_items = items[start_index:end_index]
    
    return {
        'items': page_items,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'page_size': page_size,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'previous_page': page - 1 if page > 1 else None,
        }
    }


def create_paginated_response(data: Dict[str, Any], status: int = 200) -> JsonResponse:
    """
    Create a paginated JSON response.
    
    Args:
        data: Pagination data dictionary
        status: HTTP status code
        
    Returns:
        JsonResponse with paginated data
    """
    return JsonResponse(data, status=status)


def get_pagination_links(request: HttpRequest, current_page: int, 
                        total_pages: int, page_size: int) -> Dict[str, Optional[str]]:
    """
    Generate pagination links for API responses.
    
    Args:
        request: Django HttpRequest object
        current_page: Current page number
        total_pages: Total number of pages
        page_size: Items per page
        
    Returns:
        Dictionary with pagination links
    """
    base_url = request.build_absolute_uri(request.path)
    query_params = request.GET.copy()
    
    def build_url(page_num: Optional[int]) -> Optional[str]:
        if page_num is None:
            return None
        
        query_params['page'] = page_num
        query_params['page_size'] = page_size
        return f"{base_url}?{query_params.urlencode()}"
    
    return {
        'first': build_url(1) if current_page > 1 else None,
        'last': build_url(total_pages) if current_page < total_pages else None,
        'next': build_url(current_page + 1) if current_page < total_pages else None,
        'previous': build_url(current_page - 1) if current_page > 1 else None,
        'current': build_url(current_page)
    }


def paginate_with_links(request: HttpRequest, queryset: Any, 
                       page: int, page_size: int) -> Dict[str, Any]:
    """
    Paginate queryset with pagination links.
    
    Args:
        request: Django HttpRequest object
        queryset: Django queryset to paginate
        page: Page number
        page_size: Items per page
        
    Returns:
        Dictionary with paginated data and links
    """
    paginated_data = paginate_queryset(queryset, page, page_size)
    pagination_info = paginated_data['pagination']
    
    links = get_pagination_links(
        request, 
        pagination_info['current_page'],
        pagination_info['total_pages'],
        pagination_info['page_size']
    )
    
    return {
        'items': paginated_data['items'],
        'pagination': pagination_info,
        'links': links
    }


def validate_pagination_params(page: int, page_size: int, 
                              max_page_size: int = 100) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number
        page_size: Items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of validated (page, page_size)
    """
    # Ensure page is at least 1
    page = max(1, page)
    
    # Ensure page_size is within bounds
    page_size = max(1, min(page_size, max_page_size))
    
    return page, page_size


def get_offset_and_limit(page: int, page_size: int) -> Tuple[int, int]:
    """
    Convert page-based pagination to offset and limit.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Tuple of (offset, limit)
    """
    offset = (page - 1) * page_size
    return offset, page_size


def calculate_page_info(total_items: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    Calculate pagination information.
    
    Args:
        total_items: Total number of items
        page: Current page number
        page_size: Items per page
        
    Returns:
        Dictionary with pagination information
    """
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    
    return {
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'page_size': page_size,
        'has_next': page < total_pages,
        'has_previous': page > 1,
        'next_page': page + 1 if page < total_pages else None,
        'previous_page': page - 1 if page > 1 else None,
        'start_index': (page - 1) * page_size + 1 if total_items > 0 else 0,
        'end_index': min(page * page_size, total_items)
    }