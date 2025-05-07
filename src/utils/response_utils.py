"""
Response Utilities for APE-Core

This module provides utilities for formatting and handling responses.
"""

from typing import Dict, List, Any, Optional, Union

def format_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Format a successful response
    
    Args:
        data: Response data
        message: Optional success message
        
    Returns:
        Formatted success response
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response

def format_error_response(error: Union[str, Exception], code: Optional[int] = None) -> Dict[str, Any]:
    """
    Format an error response
    
    Args:
        error: Error message or exception
        code: Optional error code
        
    Returns:
        Formatted error response
    """
    error_message = str(error) if error else "Unknown error"
    
    response = {
        "success": False,
        "error": error_message
    }
    
    if code:
        response["code"] = code
    
    return response

def format_list_response(
    items: List[Any],
    total: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Format a response with a list of items
    
    Args:
        items: List of items
        total: Optional total count of items
        page: Optional current page number
        page_size: Optional page size
        
    Returns:
        Formatted list response
    """
    response = {
        "success": True,
        "data": {
            "items": items,
            "count": len(items)
        }
    }
    
    if total is not None:
        response["data"]["total"] = total
    
    if page is not None:
        response["data"]["page"] = page
    
    if page_size is not None:
        response["data"]["page_size"] = page_size
    
    return response

def extract_error_message(error: Any) -> str:
    """
    Extract error message from various error types
    
    Args:
        error: Error object
        
    Returns:
        Error message string
    """
    if isinstance(error, str):
        return error
    elif isinstance(error, Exception):
        return str(error)
    elif isinstance(error, dict) and "message" in error:
        return error["message"]
    elif isinstance(error, dict) and "error" in error:
        return error["error"]
    else:
        return str(error)