"""
LLM Service for APE-Core

This module provides the core LLM service functionality for interacting with
different LLM providers (Claude) with proper header handling.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union, Callable

# Define model enums
class LLMModel:
    """Available LLM models"""
    CLAUDE = "claude-3-opus-20240229"
    CLAUDE_INSTANT = "claude-3-haiku-20240307"
    QWEN = "qwen:72b"
    GPT35 = "gpt-3.5-turbo"

class MessageRole:
    """Message roles in a conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class LLMService:
    """Service for interacting with LLM APIs"""
    
    def __init__(self):
        """Initialize the LLM service"""
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables"""
        # Load from environment variables
        self.endpoint = os.environ.get("APE_LLM_ENDPOINT", "http://localhost:8000/api/chat")
        self.default_model = os.environ.get("DEFAULT_MODEL", LLMModel.CLAUDE)
        self.api_key = os.environ.get("APE_OPENROUTER_API_KEY", "dummy-api-key")
        self.anthropic_key = os.environ.get("APE_ANTHROPIC_API_KEY", "dummy-anthropic-key")
    
    def get_active_model(self) -> str:
        """Get the currently active LLM model"""
        return self.default_model
    
    def set_active_model(self, model: str):
        """Set the active LLM model"""
        self.default_model = model
    
    def get_available_models(self) -> List[str]:
        """Get all available LLM models"""
        return [LLMModel.CLAUDE, LLMModel.CLAUDE_INSTANT]
    
    def send_request(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a request to the LLM and get a response
        
        Args:
            messages: List of message objects with role and content
            model: Model to use (defaults to the active model)
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            system_prompt: System prompt to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing success status, data and optional error
        """
        try:
            # Use provided model or default
            model_to_use = model or self.default_model
            
            # Format messages for API
            formatted_messages = self._format_messages_for_api(messages, system_prompt)
            
            # Send HTTP request
            response = self._send_http_request(
                formatted_messages,
                model_to_use,
                temperature,
                max_tokens,
                stream,
                **kwargs
            )
            
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_messages_for_api(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Format messages for the API
        
        Args:
            messages: Raw messages
            system_prompt: Optional system prompt
            
        Returns:
            Formatted messages
        """
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": MessageRole.SYSTEM,
                "content": system_prompt
            })
        
        # Add user messages
        for message in messages:
            formatted_messages.append({
                "role": message.get("role", MessageRole.USER),
                "content": message.get("content", "")
            })
        
        return formatted_messages
    
    def _send_http_request(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send HTTP request to LLM API
        
        Args:
            messages: Formatted messages
            model: Model to use
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Processed API response
        """
        # Build request body
        request_body = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # Add any additional parameters
        if kwargs:
            request_body.update(kwargs)
        
        # Set up headers based on model
        headers = {"Content-Type": "application/json"}
        
        # Add authentication headers based on model
        if model in [LLMModel.CLAUDE, LLMModel.CLAUDE_INSTANT]:
            # Anthropic Claude models header setup
            headers["x-api-key"] = self.anthropic_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            # OpenRouter header setup for all other models
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["HTTP-Referer"] = "https://openrouter.ai/docs"
            headers["X-Title"] = "APE (Agentic Pipeline Engine)"
            
            # Add any other headers if needed
        
        # Debug messages removed for production
        
        # Send request
        response = requests.post(
            self.endpoint,
            json=request_body,
            headers=headers
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Process response based on model
        return self._process_response(data, model)
    
    def _process_response(self, response_data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """
        Process API response
        
        Args:
            response_data: Raw API response
            model: Model used for the request
            
        Returns:
            Processed response
        """
        # Check response format based on model
        if model in [LLMModel.CLAUDE, LLMModel.CLAUDE_INSTANT]:
            # Claude response format
            content = response_data.get("content", "") or response_data.get("completion", "")
            
            return {
                "message": {
                    "role": MessageRole.ASSISTANT,
                    "content": content
                },
                "usage": response_data.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }),
                "metadata": response_data.get("metadata", {})
            }
        else:
            # OpenRouter/OpenAI format
            choices = response_data.get("choices", [{}])
            content = choices[0].get("message", {}).get("content", "") if choices else ""
            
            return {
                "message": {
                    "role": MessageRole.ASSISTANT,
                    "content": content
                },
                "usage": response_data.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }),
                "metadata": response_data.get("metadata", {})
            }
    
    def get_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Get a simple completion from the LLM for a prompt
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with success status, completion text and optional error
        """
        # Create a simple message with the prompt
        messages = [{"role": MessageRole.USER, "content": prompt}]
        
        # Send the request
        result = self.send_request(messages, **kwargs)
        
        if result["success"]:
            return {
                "success": True,
                "data": result["data"]["message"]["content"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Failed to get completion")
            }