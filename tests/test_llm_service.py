"""
Unit tests for LLM Service

This module contains unit tests for the LLM Service.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to test
from src.core.llm_service import LLMService, LLMModel, MessageRole


class TestLLMService(unittest.TestCase):
    """Tests for the LLMService class"""

    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["APE_LLM_ENDPOINT"] = "https://test-endpoint.com/api"
        os.environ["DEFAULT_MODEL"] = LLMModel.LLAMA4
        os.environ["APE_OPENROUTER_API_KEY"] = "test-api-key"
        os.environ["APE_ANTHROPIC_API_KEY"] = "test-anthropic-key"
        
        # Initialize the service
        self.llm_service = LLMService()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test environment variables
        if "APE_LLM_ENDPOINT" in os.environ:
            del os.environ["APE_LLM_ENDPOINT"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
        if "APE_OPENROUTER_API_KEY" in os.environ:
            del os.environ["APE_OPENROUTER_API_KEY"]
        if "APE_ANTHROPIC_API_KEY" in os.environ:
            del os.environ["APE_ANTHROPIC_API_KEY"]
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.llm_service.endpoint, "https://test-endpoint.com/api")
        self.assertEqual(self.llm_service.default_model, LLMModel.LLAMA4)
        self.assertEqual(self.llm_service.api_key, "test-api-key")
        self.assertEqual(self.llm_service.anthropic_key, "test-anthropic-key")
    
    def test_get_active_model(self):
        """Test getting active model"""
        self.assertEqual(self.llm_service.get_active_model(), LLMModel.LLAMA4)
    
    def test_set_active_model(self):
        """Test setting active model"""
        self.llm_service.set_active_model(LLMModel.CLAUDE)
        self.assertEqual(self.llm_service.get_active_model(), LLMModel.CLAUDE)
    
    def test_get_available_models(self):
        """Test getting available models"""
        models = self.llm_service.get_available_models()
        self.assertEqual(len(models), 5)
        self.assertIn(LLMModel.CLAUDE, models)
        self.assertIn(LLMModel.CLAUDE_INSTANT, models)
        self.assertIn(LLMModel.LLAMA4, models)
        self.assertIn(LLMModel.QWEN, models)
        self.assertIn(LLMModel.GPT35, models)
    
    def test_format_messages_for_api_without_system_prompt(self):
        """Test message formatting without system prompt"""
        messages = [
            {"role": MessageRole.USER, "content": "Hello"},
            {"role": MessageRole.ASSISTANT, "content": "Hi there"}
        ]
        
        formatted = self.llm_service._format_messages_for_api(messages)
        
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]["role"], MessageRole.USER)
        self.assertEqual(formatted[0]["content"], "Hello")
        self.assertEqual(formatted[1]["role"], MessageRole.ASSISTANT)
        self.assertEqual(formatted[1]["content"], "Hi there")
    
    def test_format_messages_for_api_with_system_prompt(self):
        """Test message formatting with system prompt"""
        messages = [
            {"role": MessageRole.USER, "content": "Hello"}
        ]
        system_prompt = "You are a helpful assistant"
        
        formatted = self.llm_service._format_messages_for_api(messages, system_prompt)
        
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]["role"], MessageRole.SYSTEM)
        self.assertEqual(formatted[0]["content"], system_prompt)
        self.assertEqual(formatted[1]["role"], MessageRole.USER)
        self.assertEqual(formatted[1]["content"], "Hello")
    
    @patch('requests.post')
    def test_send_http_request_openrouter(self, mock_post):
        """Test sending HTTP request to OpenRouter"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_post.return_value = mock_response
        
        # Test data
        messages = [{"role": MessageRole.USER, "content": "Hello"}]
        model = LLMModel.LLAMA4
        temperature = 0.7
        max_tokens = 1000
        stream = False
        
        # Call method
        response = self.llm_service._send_http_request(messages, model, temperature, max_tokens, stream)
        
        # Verify
        mock_post.assert_called_once()
        self.assertEqual(response["message"]["role"], MessageRole.ASSISTANT)
        self.assertEqual(response["message"]["content"], "This is a test response")
        self.assertEqual(response["usage"]["prompt_tokens"], 10)
        self.assertEqual(response["usage"]["completion_tokens"], 5)
        self.assertEqual(response["usage"]["total_tokens"], 15)
    
    @patch('requests.post')
    def test_send_http_request_claude(self, mock_post):
        """Test sending HTTP request to Claude"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": "This is a Claude response",
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 6,
                "total_tokens": 18
            }
        }
        mock_post.return_value = mock_response
        
        # Test data
        messages = [{"role": MessageRole.USER, "content": "Hello Claude"}]
        model = LLMModel.CLAUDE
        temperature = 0.8
        max_tokens = 1500
        stream = False
        
        # Call method
        response = self.llm_service._send_http_request(messages, model, temperature, max_tokens, stream)
        
        # Verify
        mock_post.assert_called_once()
        
        # Verify headers contain Anthropic-specific headers
        headers = mock_post.call_args.kwargs['headers']
        self.assertEqual(headers["x-api-key"], "test-anthropic-key")
        self.assertEqual(headers["anthropic-version"], "2023-06-01")
        
        # Verify response
        self.assertEqual(response["message"]["role"], MessageRole.ASSISTANT)
        self.assertEqual(response["message"]["content"], "This is a Claude response")
        self.assertEqual(response["usage"]["prompt_tokens"], 12)
        self.assertEqual(response["usage"]["completion_tokens"], 6)
        self.assertEqual(response["usage"]["total_tokens"], 18)
    
    @patch('requests.post')
    def test_send_http_request_error_handling(self, mock_post):
        """Test error handling in HTTP request"""
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized")
        mock_post.return_value = mock_response
        
        # Test data
        messages = [{"role": MessageRole.USER, "content": "Test message"}]
        model = LLMModel.LLAMA4
        temperature = 0.7
        max_tokens = 1000
        stream = False
        
        # Mock response objects for the exception
        mock_response.json.return_value = {"error": "unauthorized"}
        
        # Call method with error situation
        with patch.object(self.llm_service, '_process_response') as mock_process:
            mock_process.return_value = {"mock": "processed_response"}
            with self.assertRaises(requests.exceptions.HTTPError):
                self.llm_service._send_http_request(messages, model, temperature, max_tokens, stream)
    
    @patch.object(LLMService, 'send_request')
    def test_get_completion(self, mock_send_request):
        """Test get_completion method"""
        # Setup mock response
        mock_send_request.return_value = {
            "success": True,
            "data": {
                "message": {
                    "content": "This is a completion response"
                }
            }
        }
        
        # Call method
        result = self.llm_service.get_completion("Test prompt")
        
        # Verify
        mock_send_request.assert_called_once()
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], "This is a completion response")
    
    @patch.object(LLMService, 'send_request')
    def test_get_completion_error(self, mock_send_request):
        """Test get_completion method with error"""
        # Setup mock error response
        mock_send_request.return_value = {
            "success": False,
            "error": "Something went wrong"
        }
        
        # Call method
        result = self.llm_service.get_completion("Test prompt")
        
        # Verify
        mock_send_request.assert_called_once()
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Something went wrong")


if __name__ == '__main__':
    unittest.main()