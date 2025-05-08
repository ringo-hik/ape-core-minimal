"""
HTTP Utilities for APE-Core

This module provides utilities for HTTP operations and error handling.
"""

import requests
from typing import Dict, Any, Optional, Tuple, Union


def safe_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    auth: Optional[Tuple[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: Union[float, Tuple[float, float]] = (5, 30)
) -> Dict[str, Any]:
    """
    Make a safe HTTP request with improved error handling
    
    Args:
        method: HTTP method ('get', 'post', 'put', 'delete', etc.)
        url: URL to request
        headers: Optional headers to include
        auth: Optional Basic Auth tuple (username, password)
        json: Optional JSON data for the request
        data: Optional form data or raw data
        params: Optional URL parameters
        timeout: Request timeout (connect_timeout, read_timeout)
        
    Returns:
        Dictionary with success status, response data, and error information
    """
    try:
        # Use session for better performance with connection pooling
        with requests.Session() as session:
            # Set authentication if provided
            if auth:
                session.auth = auth
            
            # Set headers if provided
            if headers:
                session.headers.update(headers)
            
            # Select the appropriate HTTP method
            request_method = getattr(session, method.lower())
            
            # Make the request
            response = request_method(
                url,
                json=json,
                data=data,
                params=params,
                timeout=timeout
            )
            
            # Raise for status to catch HTTP errors
            response.raise_for_status()
            
            # Try to parse as JSON if the response has content
            if response.text:
                try:
                    data = response.json()
                except ValueError:
                    # Not JSON data, return the text
                    data = response.text
            else:
                # No content in response
                data = None
            
            # Return successful response
            return {
                "success": True,
                "status_code": response.status_code,
                "data": data,
                "headers": dict(response.headers),
                "url": response.url
            }
    
    except requests.exceptions.HTTPError as e:
        # HTTP error occurred (4xx, 5xx)
        status_code = e.response.status_code if hasattr(e, 'response') else None
        
        # Try to get error details from response
        error_detail = None
        if hasattr(e, 'response') and e.response.text:
            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.text
        
        return {
            "success": False,
            "status_code": status_code,
            "error": f"HTTP Error: {str(e)}",
            "error_type": "http_error",
            "error_detail": error_detail,
            "url": url
        }
    
    except requests.exceptions.ConnectionError as e:
        # Connection error occurred
        return {
            "success": False,
            "error": f"Connection Error: Could not connect to {url}. {str(e)}",
            "error_type": "connection_error",
            "url": url
        }
    
    except requests.exceptions.Timeout as e:
        # Timeout error occurred
        return {
            "success": False,
            "error": f"Timeout Error: Request to {url} timed out. {str(e)}",
            "error_type": "timeout_error",
            "url": url
        }
    
    except requests.exceptions.RequestException as e:
        # General request exception occurred
        return {
            "success": False,
            "error": f"Request Error: {str(e)}",
            "error_type": "request_error",
            "url": url
        }
    
    except Exception as e:
        # Unexpected exception occurred
        return {
            "success": False,
            "error": f"Unexpected Error: {str(e)}",
            "error_type": "unexpected_error",
            "url": url
        }


def format_error_message(result: Dict[str, Any]) -> str:
    """
    Format a readable error message from an error response
    
    Args:
        result: Error result from safe_request
        
    Returns:
        Formatted error message
    """
    error_type = result.get("error_type", "unknown")
    error_msg = result.get("error", "Unknown error occurred")
    status_code = result.get("status_code")
    
    if error_type == "http_error" and status_code:
        if status_code == 400:
            return f"Bad Request (400): {error_msg}"
        elif status_code == 401:
            return f"Unauthorized (401): Invalid authentication credentials"
        elif status_code == 403:
            return f"Forbidden (403): You don't have permission to access this resource"
        elif status_code == 404:
            return f"Not Found (404): The requested resource was not found"
        elif status_code == 429:
            return f"Too Many Requests (429): Rate limit exceeded, please try again later"
        elif status_code >= 500:
            return f"Server Error ({status_code}): The server is experiencing issues"
        else:
            return f"HTTP Error ({status_code}): {error_msg}"
    
    return error_msg