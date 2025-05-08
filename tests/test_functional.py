"""
Functional Test for APE Core

This module contains functional tests that test core components working together.
Tests are designed to work with real OpenRouter models.
"""

import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from src.core.llm_service import LLMService, LLMModel, MessageRole
from src.agents.jira_agent import JiraAgent
from src.agents.orchestrator import Orchestrator


class TestAPECoreFunctional(unittest.TestCase):
    """Functional tests for APE Core"""
    
    def setUp(self):
        """Set up test environment"""
        # Check for API keys or skip tests
        self.skip_real_api = False
        
        if "APE_OPENROUTER_API_KEY" not in os.environ or not os.environ["APE_OPENROUTER_API_KEY"]:
            print("WARNING: No OpenRouter API key found. Skipping real API tests.")
            self.skip_real_api = True
        
        # Initialize services
        self.llm_service = LLMService()
        self.orchestrator = Orchestrator(self.llm_service)
        
        # Mock Jira agent for tests
        self.jira_agent = self._create_mock_jira_agent()
        self.orchestrator.register_agent("jira", self.jira_agent)
    
    def _create_mock_jira_agent(self):
        """Create a mock Jira agent for testing"""
        # Create mock agent
        mock_jira = MagicMock(spec=JiraAgent)
        
        # Mock capabilities
        mock_jira.get_capabilities.return_value = [
            "get_issue", "create_issue", "update_issue", "search_issues", 
            "add_comment", "get_projects", "get_issue_types"
        ]
        
        # Mock validate_request
        mock_jira.validate_request.return_value = True
        
        # Mock process method
        def mock_process(request):
            action = request.get("action")
            
            if action == "create_issue":
                return {
                    "success": True,
                    "data": {
                        "key": "TEST-123",
                        "id": "10001",
                        "self": "https://test-jira.com/rest/api/2/issue/10001"
                    }
                }
            elif action == "get_issue":
                return {
                    "success": True,
                    "data": {
                        "key": "TEST-123",
                        "fields": {
                            "summary": "Test Issue",
                            "description": "This is a test issue",
                            "status": {"name": "Open"}
                        }
                    }
                }
            elif action == "add_comment":
                return {
                    "success": True,
                    "data": {
                        "id": "10001",
                        "body": request.get("comment", "")
                    }
                }
            elif action == "get_projects":
                return {
                    "success": True,
                    "data": [
                        {"key": "TEST", "name": "Test Project"}
                    ]
                }
            else:
                return {"success": False, "error": f"Unsupported action: {action}"}
        
        mock_jira.process.side_effect = mock_process
        
        return mock_jira
    
    def test_llm_get_completion(self):
        """Test LLM get_completion with real API if available"""
        if self.skip_real_api:
            self.skipTest("Skipping real API test")
        
        # Simple prompt for testing
        prompt = "What is the capital of France? Answer in one word."
        
        # Get completion
        result = self.llm_service.get_completion(prompt)
        
        # Verify
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["data"])
        self.assertIn("Paris", result["data"])
    
    def test_llm_send_request(self):
        """Test LLM send_request with real API if available"""
        if self.skip_real_api:
            self.skipTest("Skipping real API test")
        
        # Test messages
        messages = [
            {"role": MessageRole.USER, "content": "What is the capital of Italy? Answer in one word."}
        ]
        
        # Send request
        result = self.llm_service.send_request(messages)
        
        # Verify
        self.assertTrue(result["success"])
        self.assertIn("message", result["data"])
        self.assertEqual(result["data"]["message"]["role"], MessageRole.ASSISTANT)
        self.assertIn("Rome", result["data"]["message"]["content"])
    
    def test_orchestrator_execute_workflow(self):
        """Test orchestrator executing a workflow with LLM and Jira"""
        # Define workflow
        workflow_steps = [
            {
                "agent": "jira",
                "action": "create_issue",
                "parameters": {
                    "fields": {
                        "project": {"key": "TEST"},
                        "summary": "Test Issue",
                        "description": "This is a test issue",
                        "issuetype": {"id": "10001"}
                    }
                },
                "output_key": "issue"
            },
            {
                "agent": "jira",
                "action": "get_issue",
                "parameters": {"issue_key": "${issue.key}"},
                "output_key": "issue_details"
            },
            {
                "agent": "jira",
                "action": "add_comment",
                "parameters": {
                    "issue_key": "${issue.key}",
                    "comment": "This is a test comment"
                },
                "output_key": "comment"
            }
        ]
        
        # Register workflow
        self.orchestrator.register_workflow("test_workflow", workflow_steps)
        
        # Execute workflow
        result = self.orchestrator.execute_workflow("test_workflow")
        
        # Verify
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 3)
        self.assertTrue(result["results"][0]["success"])
        self.assertTrue(result["results"][1]["success"])
        self.assertTrue(result["results"][2]["success"])
        
        # Verify context
        self.assertIn("issue", result["context"])
        self.assertIn("issue_details", result["context"])
        self.assertIn("comment", result["context"])
        
        # Verify Jira agent was called correctly
        calls = self.jira_agent.process.call_args_list
        self.assertEqual(len(calls), 3)
        
        # Verify create issue call
        create_call = calls[0][0][0]
        self.assertEqual(create_call["action"], "create_issue")
        
        # Verify get issue call
        get_call = calls[1][0][0]
        self.assertEqual(get_call["action"], "get_issue")
        self.assertEqual(get_call["issue_key"], "TEST-123")  # From mock response
        
        # Verify add comment call
        comment_call = calls[2][0][0]
        self.assertEqual(comment_call["action"], "add_comment")
        self.assertEqual(comment_call["issue_key"], "TEST-123")  # From mock response
        self.assertEqual(comment_call["comment"], "This is a test comment")
    
    @patch.object(LLMService, 'send_request')
    def test_workflow_with_llm(self, mock_send_request):
        """Test orchestrator with LLM for generating content"""
        # Mock LLM response
        mock_send_request.return_value = {
            "success": True,
            "data": {
                "message": {
                    "content": "Bug: Unable to login\nThe login system is not working properly."
                }
            }
        }
        
        # Define workflow
        workflow_steps = [
            {
                "agent": "jira",
                "action": "create_issue",
                "parameters": {
                    "fields": {
                        "project": {"key": "TEST"},
                        "summary": "LLM Generated Issue",
                        "description": "LLM will update this",
                        "issuetype": {"id": "10002"}  # Bug type
                    }
                },
                "output_key": "issue"
            }
        ]
        
        # Register workflow
        self.orchestrator.register_workflow("llm_workflow", workflow_steps)
        
        # Execute workflow
        result = self.orchestrator.execute_workflow("llm_workflow")
        
        # Verify
        self.assertTrue(result["success"])
        self.assertTrue(result["results"][0]["success"])
        
        # Verify Jira agent was called correctly
        self.jira_agent.process.assert_called_once()
        call_args = self.jira_agent.process.call_args[0][0]
        self.assertEqual(call_args["action"], "create_issue")
        self.assertEqual(call_args["fields"]["project"]["key"], "TEST")
        self.assertEqual(call_args["fields"]["summary"], "LLM Generated Issue")
    
    def test_plan_workflow(self):
        """Test planning a workflow using LLM"""
        # Set up mock LLM response for workflow planning
        mock_response = """
        I'll create a workflow to help with this task.
        
        ```json
        [
            {
                "agent": "jira",
                "action": "create_issue",
                "parameters": {
                    "fields": {
                        "project": {"key": "TEST"},
                        "summary": "Planned Issue",
                        "description": "This issue was created by planned workflow",
                        "issuetype": {"id": "10001"}
                    }
                },
                "output_key": "issue"
            },
            {
                "agent": "jira",
                "action": "add_comment",
                "parameters": {
                    "issue_key": "${issue.key}",
                    "comment": "Automatic comment from planned workflow"
                },
                "output_key": "comment"
            }
        ]
        ```
        """
        
        # Mock the LLM service send_request method
        with patch.object(self.llm_service, 'send_request') as mock_send:
            mock_send.return_value = {
                "success": True,
                "data": {
                    "message": {
                        "content": mock_response
                    }
                }
            }
            
            # Plan workflow
            result = self.orchestrator.plan_workflow("Create an issue and add a comment")
            
            # Verify
            self.assertTrue(result["success"])
            self.assertIn("workflow_id", result["data"])
            self.assertEqual(len(result["data"]["steps"]), 2)
            
            # Verify steps
            steps = result["data"]["steps"]
            self.assertEqual(steps[0]["agent"], "jira")
            self.assertEqual(steps[0]["action"], "create_issue")
            self.assertEqual(steps[0]["output_key"], "issue")
            
            self.assertEqual(steps[1]["agent"], "jira")
            self.assertEqual(steps[1]["action"], "add_comment")
            self.assertEqual(steps[1]["output_key"], "comment")
            
            # Verify workflow was registered
            workflow_id = result["data"]["workflow_id"]
            self.assertIn(workflow_id, self.orchestrator.workflows)
            
            # Execute the planned workflow
            exec_result = self.orchestrator.execute_workflow(workflow_id)
            
            # Verify execution
            self.assertTrue(exec_result["success"])
            self.assertEqual(len(exec_result["results"]), 2)
            self.assertTrue(exec_result["results"][0]["success"])
            self.assertTrue(exec_result["results"][1]["success"])


if __name__ == '__main__':
    unittest.main()