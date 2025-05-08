"""
Jira Agent for APE-Core

This module provides integration with Jira for issue tracking and project management.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from ..core.agent_interface import ServiceAgent

class JiraAgent(ServiceAgent):
    """Agent for interacting with Jira"""
    
    def __init__(self):
        """Initialize the Jira agent"""
        self.base_url = os.environ.get("APE_JIRA_URL", "https://internal-jira-instance.com")
        self.api_token = os.environ.get("APE_JIRA_API_TOKEN", "dummy-jira-token")
        self.username = os.environ.get("APE_JIRA_USERNAME", "jira-user")
        self.project_key = os.environ.get("APE_JIRA_PROJECT_KEY", "APE")
        
        # 이미 이메일 형식이므로 그대로 사용
        self.auth = (self.username, self.api_token)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Jira-related request
        
        Args:
            request: The request to process
            
        Returns:
            Response dictionary
        """
        if not self.validate_request(request):
            return {"success": False, "error": "Invalid request format"}
        
        action = request.get("action", "")
        
        if action == "get_issue":
            return self.get_issue(request.get("issue_key", ""))
        elif action == "create_issue":
            # 직접 필드가 제공되면 사용하고, 그렇지 않으면 개별 값 사용
            if "fields" in request:
                return self.create_issue_with_fields(request.get("fields", {}))
            else:
                return self.create_issue(
                    request.get("summary", ""),
                    request.get("description", ""),
                    request.get("issue_type", "Task"),
                    request.get("priority", "Medium"),
                    request.get("labels", []),
                    request.get("components", [])
                )
        elif action == "update_issue":
            return self.update_issue(
                request.get("issue_key", ""),
                request.get("fields", {})
            )
        elif action == "search_issues":
            return self.search_issues(
                request.get("jql", ""),
                request.get("max_results", 50),
                request.get("start_at", 0)
            )
        elif action == "add_comment":
            return self.add_comment(
                request.get("issue_key", ""),
                request.get("comment", "")
            )
        elif action == "get_projects":
            return self.get_projects()
        elif action == "get_issue_types":
            return self.get_issue_types()
        else:
            return {"success": False, "error": f"Unsupported action: {action}"}
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capability strings
        """
        return [
            "get_issue",
            "create_issue",
            "update_issue",
            "search_issues",
            "add_comment",
            "get_projects",
            "get_issue_types"
        ]
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate if a request can be processed by this agent
        
        Args:
            request: The request to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        if not isinstance(request, dict):
            return False
        
        if "action" not in request:
            return False
        
        action = request.get("action", "")
        
        if action not in self.get_capabilities():
            return False
            
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate with Jira
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            # Use session for better performance
            with requests.Session() as session:
                session.auth = self.auth
                session.headers.update(self.headers)
                
                response = session.get(
                    f"{self.base_url}/rest/api/2/myself",
                    timeout=(5, 30)  # Connect timeout: 5s, Read timeout: 30s
                )
            
            # Simply check status code
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Any request exception means authentication failed
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about Jira service
        
        Returns:
            Service information
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/2/serverInfo",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get service info: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a resource in Jira
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Created resource data
        """
        if resource_type == "issue":
            return self.create_issue(
                data.get("summary", ""),
                data.get("description", ""),
                data.get("issue_type", "Task"),
                data.get("priority", "Medium"),
                data.get("labels", []),
                data.get("components", [])
            )
        elif resource_type == "comment":
            return self.add_comment(
                data.get("issue_key", ""),
                data.get("body", "")
            )
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource from Jira
        
        Args:
            resource_type: Type of resource to get
            resource_id: ID of the resource
            
        Returns:
            Resource data
        """
        if resource_type == "issue":
            return self.get_issue(resource_id)
        elif resource_type == "project":
            return self.get_project(resource_id)
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a resource in Jira
        
        Args:
            resource_type: Type of resource to update
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Updated resource data
        """
        if resource_type == "issue":
            return self.update_issue(resource_id, data)
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource in Jira
        
        Args:
            resource_type: Type of resource to delete
            resource_id: ID of the resource
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if resource_type == "issue":
                response = requests.delete(
                    f"{self.base_url}/rest/api/2/issue/{resource_id}",
                    auth=self.auth,
                    headers=self.headers
                )
                
                return response.status_code in [200, 204]
            else:
                return False
        except Exception:
            return False
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get details of a Jira issue
        
        Args:
            issue_key: Key of the issue
            
        Returns:
            Issue details
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/2/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get issue: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_issue_with_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Jira issue with custom fields
        
        Args:
            fields: Fields to use for the issue
            
        Returns:
            Created issue data
        """
        try:
            payload = {"fields": fields}
            
            # 디버깅을 위한 로그
            print(f"Create issue payload (custom fields): {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/rest/api/2/issue",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            print(f"Create issue response status: {response.status_code}")
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                    return {"success": False, "error": f"Failed to create issue: {response.status_code} - {error_detail}"}
                except:
                    return {"success": False, "error": f"Failed to create issue: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        labels: List[str] = None,
        components: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue
        
        Args:
            summary: Issue summary
            description: Issue description
            issue_type: Issue type (Default: Task)
            priority: Priority (Default: Medium)
            labels: List of labels
            components: List of components
            
        Returns:
            Created issue data
        """
        try:
            if labels is None:
                labels = []
            
            if components is None:
                components = []
            
            payload = {
                "fields": {
                    "project": {
                        "key": self.project_key
                    },
                    "summary": summary,
                    "description": description,
                    "issuetype": {
                        "name": issue_type
                    },
                    "labels": labels
                }
            }
            
            # 디버깅을 위한 로그
            print(f"Create issue payload: {json.dumps(payload, indent=2)}")
            
            # Add priority if specified
            if priority:
                payload["fields"]["priority"] = {
                    "name": priority
                }
            
            # Add components if specified
            if components:
                payload["fields"]["components"] = [{"name": component} for component in components]
            
            response = requests.post(
                f"{self.base_url}/rest/api/2/issue",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            print(f"Create issue response status: {response.status_code}")
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                    return {"success": False, "error": f"Failed to create issue: {response.status_code} - {error_detail}"}
                except:
                    return {"success": False, "error": f"Failed to create issue: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a Jira issue
        
        Args:
            issue_key: Key of the issue to update
            fields: Fields to update
            
        Returns:
            Updated issue data
        """
        try:
            payload = {
                "fields": fields
            }
            
            response = requests.put(
                f"{self.base_url}/rest/api/2/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code in [200, 204]:
                return {"success": True, "data": {"issue_key": issue_key}}
            else:
                return {"success": False, "error": f"Failed to update issue: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_issues(self, jql: str, max_results: int = 50, start_at: int = 0) -> Dict[str, Any]:
        """
        Search for Jira issues using JQL
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            start_at: Index of the first result to return
            
        Returns:
            Search results
        """
        try:
            payload = {
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at,
                "fields": ["summary", "description", "status", "priority", "assignee"]
            }
            
            response = requests.post(
                f"{self.base_url}/rest/api/2/search",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to search issues: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a Jira issue
        
        Args:
            issue_key: Key of the issue
            comment: Comment text
            
        Returns:
            Comment data
        """
        try:
            payload = {
                "body": comment
            }
            
            response = requests.post(
                f"{self.base_url}/rest/api/2/issue/{issue_key}/comment",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to add comment: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_projects(self) -> Dict[str, Any]:
        """
        Get list of Jira projects
        
        Returns:
            List of projects
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/2/project",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get projects: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        Get details of a Jira project
        
        Args:
            project_key: Key of the project
            
        Returns:
            Project details
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/2/project/{project_key}",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get project: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_issue_types(self) -> Dict[str, Any]:
        """
        Get list of issue types
        
        Returns:
            List of issue types
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/2/issuetype",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get issue types: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}