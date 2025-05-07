"""
Test script for LLM Service

This script tests the LLM service functionality with OpenRouter.
"""

import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import LLM service
from src.core.llm_service import LLMService, MessageRole

# Manual environment variable loading (since python-dotenv isn't installed)
def load_env_file():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value

# Load environment variables
load_env_file()

import requests

def test_llm_service():
    """Test the LLM service"""
    print("Testing LLM service...")
    
    # API 키는 .env 파일이나 환경 변수에서 불러와야 합니다
    # 테스트용 기본 API 키 설정
    if "APE_OPENROUTER_API_KEY" not in os.environ:
        os.environ["APE_OPENROUTER_API_KEY"] = "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"
    
    # 기본 모델을 Llama4로 설정
    os.environ["DEFAULT_MODEL"] = "meta-llama/llama-4-maverick"
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Print active model
    print(f"Active model: {llm_service.get_active_model()}")
    
    # Try directly with requests
    print("\nTrying direct request...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['APE_OPENROUTER_API_KEY']}",
                "HTTP-Referer": "https://openrouter.ai/docs",
                "X-Title": "APE Test"
            },
            json={
                "model": "meta-llama/llama-4-maverick",
                "messages": [{"role": "user", "content": "What is the capital of France?"}]
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with direct request: {e}")
    
    # Create a simple message
    messages = [
        {"role": MessageRole.USER, "content": "What is the capital of France?"}
    ]
    
    # Send request
    print("Sending request to LLM...")
    result = llm_service.send_request(messages)
    
    # Check result
    if result["success"]:
        print("\nResponse from LLM:")
        print("-" * 40)
        print(result["data"]["message"]["content"])
        print("-" * 40)
        
        # Print usage if available
        if "usage" in result["data"]:
            usage = result["data"]["usage"]
            print(f"\nToken usage:")
            print(f"- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"- Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"- Total tokens: {usage.get('total_tokens', 'N/A')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_llm_service()