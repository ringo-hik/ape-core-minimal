"""
Agent Interface for APE-Core

This module defines the base interfaces for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseAgent(ABC):
    """Base interface for all agents"""
    
    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response
        
        Args:
            request: The request to process
            
        Returns:
            Response dictionary
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capability strings
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate if a request can be processed by this agent
        
        Args:
            request: The request to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        pass

class DBAgent(BaseAgent):
    """Base class for database-interacting agents"""
    
    @abstractmethod
    def query(self, query_string: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a database query
        
        Args:
            query_string: The query to execute
            params: Optional parameters for the query
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the database schema
        
        Returns:
            Database schema information
        """
        pass
    
    @abstractmethod
    def sanitize_query(self, query_string: str) -> str:
        """
        Sanitize a query string for safety
        
        Args:
            query_string: The query to sanitize
            
        Returns:
            Sanitized query string
        """
        pass

class ServiceAgent(BaseAgent):
    """Base class for external service agents"""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external service
        
        Returns:
            True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the external service
        
        Returns:
            Service information
        """
        pass
    
    @abstractmethod
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a resource in the external service
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Created resource data
        """
        pass
    
    @abstractmethod
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource from the external service
        
        Args:
            resource_type: Type of resource to get
            resource_id: ID of the resource
            
        Returns:
            Resource data
        """
        pass
    
    @abstractmethod
    def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a resource in the external service
        
        Args:
            resource_type: Type of resource to update
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Updated resource data
        """
        pass
    
    @abstractmethod
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource in the external service
        
        Args:
            resource_type: Type of resource to delete
            resource_id: ID of the resource
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass