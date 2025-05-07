# APE Core

The core functionality for the Agentic Pipeline Engine (APE) system, providing integration with various services and orchestration capabilities.

## Overview

APE Core is a simplified version of the core functionality, focusing on:

1. LLM Integration
2. External Service Integration (Jira, S3/Pocket, SWDP, Bitbucket)
3. Orchestration capabilities

## Features

### LLM Service

The LLM service provides communication with LLM providers with support for:

- Static LLM configuration through environment variables
- Support for different models via the `DEFAULT_MODEL` setting
- Automatic header handling based on selected model
- Response handling for different API formats

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

Configuration is done through environment variables or a `.env` file:

```
# LLM Service
APE_LLM_ENDPOINT=https://internal-api.example.com/v1/chat/completions
DEFAULT_MODEL=claude-3-opus-20240229
APE_OPENROUTER_API_KEY=your-openrouter-key
APE_ANTHROPIC_API_KEY=your-anthropic-key

# Service specific configurations
# See .env file for all configuration options
```

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

```python
from ape_core.src.agents.jira_agent import JiraAgent

# Initialize Jira agent
jira_agent = JiraAgent()

# Create a Jira issue
result = jira_agent.process({
    "action": "create_issue",
    "summary": "Test Issue",
    "description": "This is a test issue",
    "issue_type": "Task"
})

if result["success"]:
    print(f"Issue created: {result['data']['key']}")
```

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

## Note

This is a simplified version of the APE Core functionality, focusing on key integrations and LLM service connectivity.