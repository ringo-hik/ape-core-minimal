# APE Core

The core functionality for the Agentic Pipeline Engine (APE) system, providing integration with various services and orchestration capabilities.

## Overview

APE Core is a simplified version of the core functionality, focusing on:

1. LLM Integration
2. External Service Integration (Jira, S3/Pocket, SWDP, Bitbucket)
3. Orchestration capabilities

## Setup Guide

### Prerequisites

- Python 3.8 or higher
- A valid API key for OpenRouter or your preferred LLM provider
- Network access to external APIs (or internal APIs for production)

### Installation

1. Clone this repository
2. Set up environment variables (see Configuration section)
3. Install required packages:

```bash
pip install -r requirements.txt
```

### Path Configuration

All paths in APE Core are designed to be dynamically calculated relative to the project directory, avoiding hardcoded absolute paths. The system uses the following approach to maintain path independence:

```python
# Example for calculating paths
import os
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
default_schema_path = os.path.join(base_dir, "schemas", "swdp-db.json")
```

This approach ensures that the system can run in any directory structure without hardcoded paths.

### Test Configuration

To test the LLM service or API connections:

```bash
# Run LLM service test
python test_llm.py
```

## Features

### LLM Service

The LLM service provides communication with LLM providers with support for:

- Static LLM configuration through environment variables
- Support for different models via the `DEFAULT_MODEL` setting
- Automatic header handling based on selected model
- Response handling for different API formats
- Mock responses for testing when API connections are unavailable

### Agent System

The agent system provides a framework for integrating with different services:

- Base agent interfaces
- Database agent support
- Service agent support
- Orchestration capabilities

### Integrations

The following integrations are available:

- **Jira**: Issue tracking and project management
- **Pocket (S3)**: Object storage
- **SWDP**: Software Development Platform via SQL
- **Bitbucket**: Source code management

### Orchestration

The orchestration system allows coordinating multiple agents to perform complex tasks:

- Define and register workflows
- Execute workflows with context passing
- Dynamic workflow planning using LLM

## Configuration

Configuration is done through environment variables or a `.env` file. Create a `.env` file in the project root with the following format:

```
# LLM Service Configuration
APE_LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
DEFAULT_MODEL=meta-llama/llama-4-maverick
APE_OPENROUTER_API_KEY=your-openrouter-key
APE_ANTHROPIC_API_KEY=your-anthropic-key

# Service specific configurations
# Jira Integration
APE_JIRA_URL=https://your-jira-instance.example.com
APE_JIRA_API_TOKEN=your-jira-token
APE_JIRA_USERNAME=jira-user
APE_JIRA_PROJECT_KEY=YOUR-PROJECT

# S3/Pocket Integration
APE_POCKET_ENDPOINT=https://your-s3-endpoint.example.com
APE_POCKET_ACCESS_KEY=your-access-key
APE_POCKET_SECRET_KEY=your-secret-key
APE_POCKET_REGION=your-region
APE_POCKET_DEFAULT_BUCKET=your-bucket

# SWDP Database
APE_SWDP_DB_HOST=your-db-host.example.com
APE_SWDP_DB_PORT=3306
APE_SWDP_DB_USER=db-user
APE_SWDP_DB_PASSWORD=db-password
APE_SWDP_DB_NAME=db-name

# Bitbucket Integration
APE_BITBUCKET_URL=https://your-bitbucket-instance.example.com
APE_BITBUCKET_API_TOKEN=your-bitbucket-token
APE_BITBUCKET_USERNAME=bitbucket-user
APE_BITBUCKET_WORKSPACE=your-workspace
APE_BITBUCKET_PROJECT_KEY=YOUR-PROJECT
```

For development, the system includes fallback values for all configuration settings, but for production use, you should properly configure all required values.

### Internal vs External API Configuration

The system is designed to connect to internal APIs in production environments. For development and testing, it can connect to external APIs with the appropriate configuration.

- **Production**: Use internal API endpoints with proper authentication
- **Development**: Use external API endpoints (OpenRouter, etc.) with API keys

## Directory Structure

```
ape-core/
├── schemas/             # JSON schemas for services
├── src/
│   ├── core/            # Core functionality
│   │   ├── agent_interface.py
│   │   ├── llm_service.py
│   │   └── ...
│   ├── agents/          # Agent implementations
│   │   ├── jira_agent.py
│   │   ├── pocket_agent.py
│   │   ├── swdp_agent.py
│   │   ├── bitbucket_agent.py
│   │   └── orchestrator.py
│   └── utils/           # Utility functions
│       ├── db_utils.py
│       ├── response_utils.py
│       └── ...
├── .env                 # Environment configuration
└── README.md            # Documentation
```

## Usage Examples

### LLM Service

```python
from ape_core.src.core.llm_service import LLMService

# Initialize LLM service
llm_service = LLMService()

# Send a request
result = llm_service.send_request([
    {"role": "user", "content": "Hello, how are you?"}
])

if result["success"]:
    print(result["data"]["message"]["content"])
```

### Using Jira Agent

Jira 통합을 위해 다음과 같이 설정하고 사용할 수 있습니다:

1. `.env` 파일에 Jira 접근 정보 설정:
```
# Jira Integration
APE_JIRA_URL=https://your-jira-instance.atlassian.net
APE_JIRA_API_TOKEN=your-api-token
APE_JIRA_USERNAME=your-email@example.com
APE_JIRA_PROJECT_KEY=YOUR_PROJECT
```

2. 코드에서 다음과 같이 사용:
```python
from ape_core.src.agents.jira_agent import JiraAgent

# Initialize Jira agent
jira_agent = JiraAgent()

# 방법 1: 간단한 이슈 생성
result = jira_agent.process({
    "action": "create_issue",
    "summary": "테스트 이슈",
    "description": "이슈 설명",
    "issue_type": "작업"  # Jira 설정에 따라 이슈 유형이 다를 수 있음
})

# 방법 2: ID로 이슈 유형 지정 (더 안정적)
result = jira_agent.process({
    "action": "create_issue",
    "fields": {
        "project": {
            "key": "PROJECT_KEY"
        },
        "summary": "테스트 이슈",
        "description": "이슈 설명",
        "issuetype": {
            "id": "10001"  # 이슈 유형 ID
        }
    }
})

if result["success"]:
    print(f"Issue created: {result['data']['key']}")
```

Jira Cloud에서 API 토큰을 생성하려면 다음 단계를 따르세요:
1. Atlassian 계정 페이지(https://id.atlassian.com/manage-profile/security/api-tokens)로 이동
2. '새 토큰 만들기(Create API Token)' 선택
3. 토큰에 대한 레이블 입력 및 생성
4. 생성된 토큰을 안전한 장소에 저장하고 APE_JIRA_API_TOKEN 환경 변수에 설정

### Orchestration

```python
from ape_core.src.core.llm_service import LLMService
from ape_core.src.agents.jira_agent import JiraAgent
from ape_core.src.agents.orchestrator import Orchestrator

# Initialize services
llm_service = LLMService()
jira_agent = JiraAgent()

# Initialize orchestrator
orchestrator = Orchestrator(llm_service)
orchestrator.register_agent("jira", jira_agent)

# Define a workflow
workflow_steps = [
    {
        "agent": "jira",
        "action": "get_issue",
        "parameters": {"issue_key": "APE-123"},
        "output_key": "issue"
    },
    {
        "agent": "jira",
        "action": "add_comment",
        "parameters": {
            "issue_key": "${issue.key}",
            "comment": "This issue has been processed"
        }
    }
]

# Register workflow
orchestrator.register_workflow("process_issue", workflow_steps)

# Execute workflow
result = orchestrator.execute_workflow("process_issue")
```

## Testing

### Testing the LLM Service

To test the LLM service, you can run:

```bash
python test_llm.py
```

This will attempt to connect to the configured LLM API. If the API key is invalid or the API is unavailable, the system will fall back to a mock response for development purposes.

### Testing Agent Integrations

Agent integrations require proper configuration for testing. Each agent has specific configuration requirements as detailed in the Configuration section.

## Troubleshooting

Common issues and their solutions:

1. **API Key Invalid**: Check that your API keys are valid and correctly formatted in the .env file.
2. **Path Issues**: Ensure that the system is using dynamic path calculation for file access instead of hardcoded paths.
3. **Connection Errors**: For internal API access, ensure you are on the correct network with proper access rights.

## Note

This is a simplified version of the APE Core functionality, focusing on key integrations and LLM service connectivity. For internal deployment, ensure that all services are properly configured with internal API endpoints and credentials.