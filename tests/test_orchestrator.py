"""
Unit tests for Orchestrator

This module contains unit tests for the Orchestrator.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from src.core.llm_service import LLMService
from src.core.agent_interface import BaseAgent
from src.agents.orchestrator import Orchestrator


class MockAgent(BaseAgent):
    """Mock agent for testing"""
    
    def __init__(self, name="mock", capabilities=None):
        self.name = name
        self._capabilities = capabilities or ["test_action"]
    
    def process(self, request):
        """Mock process method"""
        if not self.validate_request(request):
            return {"success": False, "error": "Invalid request"}
        
        # Return success with mock data
        return {
            "success": True, 
            "data": {
                "result": f"Processed {request.get('action')} with {self.name}",
                "request": request
            }
        }
    
    def get_capabilities(self):
        """Return capabilities"""
        return self._capabilities
    
    def validate_request(self, request):
        """Validate request"""
        if not isinstance(request, dict):
            return False
        
        if "action" not in request:
            return False
        
        if request["action"] not in self.get_capabilities():
            return False
        
        return True


class TestOrchestrator(unittest.TestCase):
    """Tests for the Orchestrator class"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock LLM service
        self.mock_llm_service = MagicMock(spec=LLMService)
        
        # Initialize orchestrator with mock LLM service
        self.orchestrator = Orchestrator(self.mock_llm_service)
        
        # Create mock agents
        self.agent1 = MockAgent("agent1", ["action1", "action2"])
        self.agent2 = MockAgent("agent2", ["action3", "action4"])
    
    def test_register_agent(self):
        """Test registering agents"""
        # Register agents
        result1 = self.orchestrator.register_agent("agent1", self.agent1)
        result2 = self.orchestrator.register_agent("agent2", self.agent2)
        
        # Verify
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertEqual(len(self.orchestrator.registered_agents), 2)
        self.assertEqual(self.orchestrator.registered_agents["agent1"], self.agent1)
        self.assertEqual(self.orchestrator.registered_agents["agent2"], self.agent2)
    
    def test_register_duplicate_agent(self):
        """Test registering duplicate agent"""
        # Register agent
        result1 = self.orchestrator.register_agent("agent1", self.agent1)
        
        # Try to register again with same name
        result2 = self.orchestrator.register_agent("agent1", MockAgent())
        
        # Verify
        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertEqual(len(self.orchestrator.registered_agents), 1)
        self.assertEqual(self.orchestrator.registered_agents["agent1"], self.agent1)
    
    def test_unregister_agent(self):
        """Test unregistering agent"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Unregister one agent
        result = self.orchestrator.unregister_agent("agent1")
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.orchestrator.registered_agents), 1)
        self.assertNotIn("agent1", self.orchestrator.registered_agents)
        self.assertIn("agent2", self.orchestrator.registered_agents)
    
    def test_unregister_nonexistent_agent(self):
        """Test unregistering nonexistent agent"""
        # Register agent
        self.orchestrator.register_agent("agent1", self.agent1)
        
        # Try to unregister nonexistent agent
        result = self.orchestrator.unregister_agent("nonexistent")
        
        # Verify
        self.assertFalse(result)
        self.assertEqual(len(self.orchestrator.registered_agents), 1)
        self.assertIn("agent1", self.orchestrator.registered_agents)
    
    def test_get_registered_agents(self):
        """Test getting registered agents"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Get registered agents
        agents = self.orchestrator.get_registered_agents()
        
        # Verify
        self.assertEqual(len(agents), 2)
        self.assertIn("agent1", agents)
        self.assertIn("agent2", agents)
    
    def test_execute_agent(self):
        """Test executing agent"""
        # Register agent
        self.orchestrator.register_agent("agent1", self.agent1)
        
        # Execute agent
        result = self.orchestrator.execute_agent("agent1", {"action": "action1", "param": "value"})
        
        # Verify
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["result"], "Processed action1 with agent1")
        self.assertEqual(result["data"]["request"]["action"], "action1")
        self.assertEqual(result["data"]["request"]["param"], "value")
        self.assertIn("_metadata", result["data"]["request"])
    
    def test_execute_nonexistent_agent(self):
        """Test executing nonexistent agent"""
        # Execute nonexistent agent
        result = self.orchestrator.execute_agent("nonexistent", {"action": "action"})
        
        # Verify
        self.assertFalse(result["success"])
        self.assertIn("Agent not found", result["error"])
    
    def test_register_workflow(self):
        """Test registering workflow"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Define workflow
        workflow_steps = [
            {
                "agent": "agent1",
                "action": "action1",
                "parameters": {"param1": "value1"},
                "output_key": "step1_result"
            },
            {
                "agent": "agent2",
                "action": "action3",
                "parameters": {"param2": "value2"},
                "output_key": "step2_result"
            }
        ]
        
        # Register workflow
        result = self.orchestrator.register_workflow("test_workflow", workflow_steps)
        
        # Verify
        self.assertTrue(result)
        self.assertIn("test_workflow", self.orchestrator.workflows)
        self.assertEqual(len(self.orchestrator.workflows["test_workflow"]["steps"]), 2)
    
    def test_register_workflow_with_invalid_agent(self):
        """Test registering workflow with invalid agent"""
        # Register agent
        self.orchestrator.register_agent("agent1", self.agent1)
        
        # Define workflow with nonexistent agent
        workflow_steps = [
            {
                "agent": "agent1",
                "action": "action1",
                "parameters": {"param1": "value1"},
                "output_key": "step1_result"
            },
            {
                "agent": "nonexistent",
                "action": "action",
                "parameters": {"param": "value"},
                "output_key": "step2_result"
            }
        ]
        
        # Register workflow
        result = self.orchestrator.register_workflow("test_workflow", workflow_steps)
        
        # Verify
        self.assertFalse(result)
        self.assertNotIn("test_workflow", self.orchestrator.workflows)
    
    def test_execute_workflow(self):
        """Test executing workflow"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Define workflow
        workflow_steps = [
            {
                "agent": "agent1",
                "action": "action1",
                "parameters": {"param1": "value1"},
                "output_key": "step1_result"
            },
            {
                "agent": "agent2",
                "action": "action3",
                "parameters": {"param2": "value2"},
                "output_key": "step2_result"
            }
        ]
        
        # Register workflow
        self.orchestrator.register_workflow("test_workflow", workflow_steps)
        
        # Execute workflow
        result = self.orchestrator.execute_workflow("test_workflow")
        
        # Verify
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 2)
        self.assertTrue(result["results"][0]["success"])
        self.assertTrue(result["results"][1]["success"])
        self.assertEqual(result["workflow_id"], "test_workflow")
        
        # Verify context
        self.assertIn("step1_result", result["context"])
        self.assertIn("step2_result", result["context"])
    
    def test_execute_workflow_with_template_parameters(self):
        """Test executing workflow with template parameters"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Define workflow with template parameters
        workflow_steps = [
            {
                "agent": "agent1",
                "action": "action1",
                "parameters": {"param1": "value1"},
                "output_key": "step1_result"
            },
            {
                "agent": "agent2",
                "action": "action3",
                "parameters": {
                    "param2": "${step1_result.result}",
                    "nested": "${step1_result.request.param1}"
                },
                "output_key": "step2_result"
            }
        ]
        
        # Register workflow
        self.orchestrator.register_workflow("template_workflow", workflow_steps)
        
        # Execute workflow
        result = self.orchestrator.execute_workflow("template_workflow")
        
        # Verify
        self.assertTrue(result["success"])
        
        # Verify template parameters were replaced
        step2_request = result["results"][1]["result"]["data"]["request"]
        self.assertEqual(step2_request["param2"], "Processed action1 with agent1")
        self.assertEqual(step2_request["nested"], "value1")
    
    def test_execute_nonexistent_workflow(self):
        """Test executing nonexistent workflow"""
        # Execute nonexistent workflow
        result = self.orchestrator.execute_workflow("nonexistent")
        
        # Verify
        self.assertFalse(result["success"])
        self.assertIn("Workflow not found", result["error"])
    
    def test_plan_workflow(self):
        """Test planning workflow with LLM"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        self.orchestrator.register_agent("agent2", self.agent2)
        
        # Mock LLM response for workflow planning
        self.mock_llm_service.send_request.return_value = {
            "success": True,
            "data": {
                "message": {
                    "content": """
                    I'll create a workflow plan to process your request.
                    
                    ```json
                    [
                        {
                            "agent": "agent1",
                            "action": "action1",
                            "parameters": {"key": "value"},
                            "output_key": "step1_result"
                        },
                        {
                            "agent": "agent2",
                            "action": "action3",
                            "parameters": {"another_key": "another_value"},
                            "output_key": "step2_result"
                        }
                    ]
                    ```
                    
                    This workflow will first use agent1 to perform action1, then use agent2 to perform action3.
                    """
                }
            }
        }
        
        # Plan workflow
        result = self.orchestrator.plan_workflow("Test query")
        
        # Verify
        self.assertTrue(result["success"])
        self.assertIn("workflow_id", result["data"])
        self.assertIn("steps", result["data"])
        self.assertEqual(len(result["data"]["steps"]), 2)
        
        # Verify workflow was registered
        self.assertTrue(result["data"]["workflow_id"] in self.orchestrator.workflows)
    
    def test_plan_workflow_extraction_failure(self):
        """Test planning workflow with LLM extraction failure"""
        # Register agents
        self.orchestrator.register_agent("agent1", self.agent1)
        
        # Mock LLM response with invalid JSON
        self.mock_llm_service.send_request.return_value = {
            "success": True,
            "data": {
                "message": {
                    "content": "I'll help you with that, but I don't have any workflow to suggest."
                }
            }
        }
        
        # Plan workflow
        result = self.orchestrator.plan_workflow("Test query")
        
        # Verify
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("extract workflow plan", result["error"])
    
    def test_evaluate_condition_simple(self):
        """Test evaluating simple condition"""
        # Test data
        context = {"value": 5, "text": "hello", "nested": {"key": "value"}}
        step_result = {"success": True, "data": {"count": 10}}
        
        # Test equal operator
        condition = {"type": "simple", "value": "context.value", "expected": 5, "operator": "eq"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
        
        # Test not equal operator
        condition = {"type": "simple", "value": "context.value", "expected": 6, "operator": "ne"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
        
        # Test greater than operator
        condition = {"type": "simple", "value": "context.value", "expected": 3, "operator": "gt"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
        
        # Test less than operator
        condition = {"type": "simple", "value": "context.value", "expected": 10, "operator": "lt"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
        
        # Test contains operator with string
        condition = {"type": "simple", "value": "context.text", "expected": "ell", "operator": "contains"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
        
        # Test exists operator
        condition = {"type": "simple", "value": "context.nested.key", "operator": "exists"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, context, step_result))
    
    def test_evaluate_custom_condition(self):
        """Test evaluating custom condition"""
        # Test data for all_success function
        step_result = {"success": True}
        condition = {"type": "custom", "function": "all_success"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, {}, step_result))
        
        # Test data for has_data function
        step_result = {"data": {"some": "data"}}
        condition = {"type": "custom", "function": "has_data"}
        self.assertTrue(self.orchestrator._evaluate_condition(condition, {}, step_result))


if __name__ == '__main__':
    unittest.main()