"""
Orchestrator for APE-Core

This module provides orchestration capabilities for coordinating multiple agents
to execute complex workflows.
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from ..core.agent_interface import BaseAgent
from ..core.llm_service import LLMService, LLMModel, MessageRole

class Orchestrator:
    """
    Orchestrator for coordinating multiple agents
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the orchestrator
        
        Args:
            llm_service: Optional LLM service instance
        """
        self.llm_service = llm_service or LLMService()
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.session_data: Dict[str, Any] = {}
        self.session_id = str(uuid.uuid4())
    
    def register_agent(self, name: str, agent: BaseAgent) -> bool:
        """
        Register an agent with the orchestrator
        
        Args:
            name: Name for the agent
            agent: Agent instance
            
        Returns:
            True if registration was successful, False otherwise
        """
        if name in self.registered_agents:
            return False
        
        self.registered_agents[name] = agent
        return True
    
    def unregister_agent(self, name: str) -> bool:
        """
        Unregister an agent from the orchestrator
        
        Args:
            name: Name of the agent to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if name not in self.registered_agents:
            return False
        
        del self.registered_agents[name]
        return True
    
    def get_registered_agents(self) -> List[str]:
        """
        Get list of registered agents
        
        Returns:
            List of agent names
        """
        return list(self.registered_agents.keys())
    
    def set_session_data(self, key: str, value: Any) -> None:
        """
        Set session data
        
        Args:
            key: Data key
            value: Data value
        """
        self.session_data[key] = value
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Get session data
        
        Args:
            key: Data key
            default: Default value if key doesn't exist
            
        Returns:
            Data value
        """
        return self.session_data.get(key, default)
    
    def execute_agent(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request on a registered agent
        
        Args:
            agent_name: Name of the agent to execute
            request: Request to execute
            
        Returns:
            Agent response
        """
        if agent_name not in self.registered_agents:
            return {"success": False, "error": f"Agent not found: {agent_name}"}
        
        agent = self.registered_agents[agent_name]
        
        try:
            # Add request metadata
            request["_metadata"] = {
                "session_id": self.session_id,
                "timestamp": time.time(),
                "agent": agent_name
            }
            
            # Execute request
            response = agent.process(request)
            
            # Add response metadata
            if isinstance(response, dict):
                if "_metadata" not in response:
                    response["_metadata"] = {}
                
                response["_metadata"].update({
                    "session_id": self.session_id,
                    "timestamp": time.time(),
                    "agent": agent_name
                })
            
            return response
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing agent {agent_name}: {str(e)}",
                "_metadata": {
                    "session_id": self.session_id,
                    "timestamp": time.time(),
                    "agent": agent_name
                }
            }
    
    def register_workflow(
        self,
        workflow_id: str,
        workflow_steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a workflow with the orchestrator
        
        Args:
            workflow_id: Unique workflow identifier
            workflow_steps: List of workflow steps
            metadata: Optional workflow metadata
            
        Returns:
            True if registration was successful, False otherwise
        """
        if workflow_id in self.workflows:
            return False
        
        # Validate workflow steps
        for step in workflow_steps:
            if "agent" not in step or "action" not in step:
                return False
            
            agent_name = step["agent"]
            if agent_name not in self.registered_agents:
                return False
        
        # Register workflow
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "steps": workflow_steps,
            "metadata": metadata or {}
        }
        
        return True
    
    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered workflow
        
        Args:
            workflow_id: Workflow identifier
            input_data: Input data for the workflow
            context: Optional context data
            
        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            return {"success": False, "error": f"Workflow not found: {workflow_id}"}
        
        workflow = self.workflows[workflow_id]
        workflow_context = context or {}
        
        # Initialize workflow execution
        execution_id = str(uuid.uuid4())
        results = []
        
        # Add input data to context
        if input_data:
            workflow_context["input"] = input_data
        
        try:
            # Execute each step
            for i, step in enumerate(workflow["steps"]):
                agent_name = step["agent"]
                action = step["action"]
                
                # Prepare request
                request = {
                    "action": action
                }
                
                # Add parameters
                if "parameters" in step:
                    params = step["parameters"]
                    
                    # Replace parameter templates
                    for key, value in params.items():
                        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                            # Template parameter
                            template_key = value[2:-1]
                            
                            if template_key in workflow_context:
                                params[key] = workflow_context[template_key]
                            elif "." in template_key:
                                # Nested parameter
                                parts = template_key.split(".")
                                current = workflow_context
                                found = True
                                
                                for part in parts:
                                    if isinstance(current, dict) and part in current:
                                        current = current[part]
                                    else:
                                        found = False
                                        break
                                
                                if found:
                                    params[key] = current
                    
                    # Add parameters to request
                    request.update(params)
                
                # Execute step
                step_result = self.execute_agent(agent_name, request)
                
                # Add to results
                results.append({
                    "step": i,
                    "agent": agent_name,
                    "action": action,
                    "success": step_result.get("success", False),
                    "result": step_result
                })
                
                # Update context with step result
                if "output_key" in step and step_result.get("success", False):
                    output_key = step["output_key"]
                    workflow_context[output_key] = step_result.get("data", {})
                
                # Check for conditional execution
                if "condition" in step and not self._evaluate_condition(step["condition"], workflow_context, step_result):
                    # Condition failed, terminate workflow or skip next steps
                    if step.get("on_failure", "terminate") == "terminate":
                        break
                
                # Check for workflow termination
                if not step_result.get("success", False) and step.get("on_failure", "terminate") == "terminate":
                    break
            
            # Return workflow results
            return {
                "success": all(result["success"] for result in results),
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "results": results,
                "context": workflow_context
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing workflow {workflow_id}: {str(e)}",
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "results": results
            }
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        context: Dict[str, Any],
        step_result: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a workflow condition
        
        Args:
            condition: Condition specification
            context: Workflow context
            step_result: Result of the current step
            
        Returns:
            True if condition is met, False otherwise
        """
        condition_type = condition.get("type", "simple")
        
        if condition_type == "simple":
            # Simple condition checking a value
            value_path = condition.get("value", "")
            expected = condition.get("expected", None)
            operator = condition.get("operator", "eq")
            
            # Get actual value
            actual = None
            
            if value_path.startswith("result."):
                # Get from step result
                path = value_path[7:].split(".")
                current = step_result
                
                for part in path:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return False
                
                actual = current
            elif value_path.startswith("context."):
                # Get from context
                path = value_path[8:].split(".")
                current = context
                
                for part in path:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return False
                
                actual = current
            
            # Compare
            if operator == "eq":
                return actual == expected
            elif operator == "ne":
                return actual != expected
            elif operator == "gt":
                return actual > expected
            elif operator == "lt":
                return actual < expected
            elif operator == "contains":
                if isinstance(actual, str) and isinstance(expected, str):
                    return expected in actual
                elif isinstance(actual, list):
                    return expected in actual
                elif isinstance(actual, dict):
                    return expected in actual
            elif operator == "exists":
                return actual is not None
        elif condition_type == "custom":
            # Custom condition function
            condition_function = condition.get("function", "")
            
            if condition_function == "all_success":
                # Check if all previous steps were successful
                return step_result.get("success", False)
            elif condition_function == "has_data":
                # Check if result has data
                return "data" in step_result and step_result["data"]
        
        return False
    
    def plan_workflow(self, query: str, available_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Plan a workflow using LLM to interpret user query
        
        Args:
            query: User query
            available_agents: Optional list of available agents
            
        Returns:
            Planned workflow
        """
        # Use available registered agents if not specified
        agents_to_use = available_agents or list(self.registered_agents.keys())
        
        # Build agent capabilities description
        agent_descriptions = []
        
        for agent_name in agents_to_use:
            if agent_name in self.registered_agents:
                agent = self.registered_agents[agent_name]
                capabilities = agent.get_capabilities()
                
                agent_descriptions.append({
                    "name": agent_name,
                    "capabilities": capabilities
                })
        
        # Prepare system prompt
        system_prompt = """You are an AI workflow planner. Your task is to create a workflow plan 
        using the available agents and their capabilities to fulfill the user's request.
        
        The workflow should be a JSON list of steps, where each step contains:
        - agent: The name of the agent to use
        - action: The action to perform
        - parameters: Parameters for the action
        - output_key: Key to store the output in the workflow context
        - on_failure: What to do if the step fails ("terminate" or "continue")
        - condition: Optional condition for execution
        
        Available agents and their capabilities:
        
        """
        
        for agent_desc in agent_descriptions:
            system_prompt += f"\nAgent: {agent_desc['name']}\n"
            system_prompt += "Capabilities:\n"
            
            for capability in agent_desc["capabilities"]:
                system_prompt += f"- {capability}\n"
        
        # Create messages
        messages = [
            {"role": MessageRole.SYSTEM, "content": system_prompt},
            {"role": MessageRole.USER, "content": f"Create a workflow plan for this request: {query}"}
        ]
        
        # Get workflow plan from LLM
        result = self.llm_service.send_request(messages)
        
        if not result["success"]:
            return {"success": False, "error": f"Failed to plan workflow: {result.get('error', 'Unknown error')}"}
        
        # Extract workflow plan from response
        response_text = result["data"]["message"]["content"]
        
        try:
            # Try to extract JSON from the response
            workflow_plan = self._extract_json_from_text(response_text)
            
            # Generate workflow ID
            workflow_id = f"generated-{str(uuid.uuid4())[:8]}"
            
            # Register workflow
            if self.register_workflow(workflow_id, workflow_plan, {"generated": True, "query": query}):
                return {
                    "success": True,
                    "data": {
                        "workflow_id": workflow_id,
                        "steps": workflow_plan,
                        "query": query
                    }
                }
            else:
                return {"success": False, "error": "Failed to register generated workflow"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract workflow plan: {str(e)}"}
    
    def _extract_json_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract JSON from text response
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON object
        """
        # Find JSON in the text
        json_start = text.find("[")
        json_end = text.rfind("]")
        
        if json_start == -1 or json_end == -1:
            # Try with curly braces
            json_start = text.find("{")
            json_end = text.rfind("}")
            
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON found in response")
            
            # Extract JSON with curly braces
            json_str = text[json_start:json_end + 1]
            workflow_steps = [json.loads(json_str)]
        else:
            # Extract JSON array
            json_str = text[json_start:json_end + 1]
            workflow_steps = json.loads(json_str)
        
        return workflow_steps