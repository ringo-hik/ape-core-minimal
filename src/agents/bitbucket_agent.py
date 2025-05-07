"""
Bitbucket Agent for APE-Core

This module provides integration with Bitbucket for source code management.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from ..core.agent_interface import ServiceAgent

class BitbucketAgent(ServiceAgent):
    """Agent for interacting with Bitbucket"""
    
    def __init__(self):
        """Initialize the Bitbucket agent"""
        self.base_url = os.environ.get("APE_BITBUCKET_URL", "https://internal-bitbucket-instance.com")
        self.api_token = os.environ.get("APE_BITBUCKET_API_TOKEN", "dummy-bitbucket-token")
        self.username = os.environ.get("APE_BITBUCKET_USERNAME", "bitbucket-user")
        self.workspace = os.environ.get("APE_BITBUCKET_WORKSPACE", "ape-workspace")
        self.project_key = os.environ.get("APE_BITBUCKET_PROJECT_KEY", "APE")
        self.auth = (self.username, self.api_token)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Bitbucket-related request
        
        Args:
            request: The request to process
            
        Returns:
            Response dictionary
        """
        if not self.validate_request(request):
            return {"success": False, "error": "Invalid request format"}
        
        action = request.get("action", "")
        
        if action == "get_repositories":
            return self.get_repositories(request.get("project_key", self.project_key))
        elif action == "get_repository":
            return self.get_repository(
                request.get("repo_slug", ""),
                request.get("project_key", self.project_key)
            )
        elif action == "get_branches":
            return self.get_branches(
                request.get("repo_slug", ""),
                request.get("project_key", self.project_key)
            )
        elif action == "get_pull_requests":
            return self.get_pull_requests(
                request.get("repo_slug", ""),
                request.get("state", "OPEN"),
                request.get("project_key", self.project_key)
            )
        elif action == "get_pull_request":
            return self.get_pull_request(
                request.get("repo_slug", ""),
                request.get("pull_request_id", ""),
                request.get("project_key", self.project_key)
            )
        elif action == "create_pull_request":
            return self.create_pull_request(
                request.get("repo_slug", ""),
                request.get("title", ""),
                request.get("description", ""),
                request.get("source_branch", ""),
                request.get("destination_branch", "master"),
                request.get("project_key", self.project_key),
                request.get("reviewers", [])
            )
        elif action == "get_commits":
            return self.get_commits(
                request.get("repo_slug", ""),
                request.get("branch", ""),
                request.get("project_key", self.project_key)
            )
        elif action == "get_file_content":
            return self.get_file_content(
                request.get("repo_slug", ""),
                request.get("file_path", ""),
                request.get("ref", "master"),
                request.get("project_key", self.project_key)
            )
        else:
            return {"success": False, "error": f"Unsupported action: {action}"}
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capability strings
        """
        return [
            "get_repositories",
            "get_repository",
            "get_branches",
            "get_pull_requests",
            "get_pull_request",
            "create_pull_request",
            "get_commits",
            "get_file_content"
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
        
        # Specific validations
        if action in ["get_repository", "get_branches", "get_pull_requests", "get_commits", "get_file_content"] and "repo_slug" not in request:
            return False
        
        if action == "get_pull_request" and ("repo_slug" not in request or "pull_request_id" not in request):
            return False
        
        if action == "create_pull_request" and (
            "repo_slug" not in request or
            "title" not in request or
            "source_branch" not in request
        ):
            return False
        
        if action == "get_file_content" and ("repo_slug" not in request or "file_path" not in request):
            return False
        
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate with Bitbucket
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/users/{self.username}",
                auth=self.auth,
                headers=self.headers
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the Bitbucket service
        
        Returns:
            Service information
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/application-properties",
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
        Create a resource in Bitbucket
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Created resource data
        """
        if resource_type == "pull_request":
            return self.create_pull_request(
                data.get("repo_slug", ""),
                data.get("title", ""),
                data.get("description", ""),
                data.get("source_branch", ""),
                data.get("destination_branch", "master"),
                data.get("project_key", self.project_key),
                data.get("reviewers", [])
            )
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource from Bitbucket
        
        Args:
            resource_type: Type of resource to get
            resource_id: ID of the resource
            
        Returns:
            Resource data
        """
        if resource_type == "repository":
            return self.get_repository(resource_id, self.project_key)
        elif resource_type == "pull_request":
            # resource_id should be in format "repo_slug/pr_id"
            if "/" in resource_id:
                repo_slug, pr_id = resource_id.split("/", 1)
                return self.get_pull_request(repo_slug, pr_id, self.project_key)
            else:
                return {"success": False, "error": "Invalid resource ID format for pull request, should be repo_slug/pr_id"}
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a resource in Bitbucket
        
        Args:
            resource_type: Type of resource to update
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Updated resource data
        """
        # Not implemented for Bitbucket yet
        return {"success": False, "error": "Update operation not implemented for Bitbucket resources"}
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource in Bitbucket
        
        Args:
            resource_type: Type of resource to delete
            resource_id: ID of the resource
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Not implemented for Bitbucket yet
        return False
    
    def get_repositories(self, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of repositories
        
        Args:
            project_key: Optional project key to filter repositories
            
        Returns:
            List of repositories
        """
        try:
            url = f"{self.base_url}/rest/api/1.0/projects"
            
            if project_key:
                url += f"/{project_key}/repos"
            
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                params={"limit": 100}
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get repositories: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_repository(self, repo_slug: str, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a repository
        
        Args:
            repo_slug: Repository slug
            project_key: Project key
            
        Returns:
            Repository details
        """
        try:
            project = project_key or self.project_key
            
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get repository: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_branches(self, repo_slug: str, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get branches in a repository
        
        Args:
            repo_slug: Repository slug
            project_key: Project key
            
        Returns:
            List of branches
        """
        try:
            project = project_key or self.project_key
            
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/branches",
                auth=self.auth,
                headers=self.headers,
                params={"limit": 100}
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get branches: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pull_requests(
        self,
        repo_slug: str,
        state: str = "OPEN",
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get pull requests in a repository
        
        Args:
            repo_slug: Repository slug
            state: Pull request state (OPEN, MERGED, DECLINED, ALL)
            project_key: Project key
            
        Returns:
            List of pull requests
        """
        try:
            project = project_key or self.project_key
            
            params = {
                "limit": 100
            }
            
            if state and state != "ALL":
                params["state"] = state
            
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/pull-requests",
                auth=self.auth,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get pull requests: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pull_request(
        self,
        repo_slug: str,
        pull_request_id: str,
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get details of a pull request
        
        Args:
            repo_slug: Repository slug
            pull_request_id: Pull request ID
            project_key: Project key
            
        Returns:
            Pull request details
        """
        try:
            project = project_key or self.project_key
            
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/pull-requests/{pull_request_id}",
                auth=self.auth,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get pull request: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_pull_request(
        self,
        repo_slug: str,
        title: str,
        description: str,
        source_branch: str,
        destination_branch: str = "master",
        project_key: Optional[str] = None,
        reviewers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a pull request
        
        Args:
            repo_slug: Repository slug
            title: PR title
            description: PR description
            source_branch: Source branch
            destination_branch: Destination branch
            project_key: Project key
            reviewers: List of reviewer usernames
            
        Returns:
            Created pull request details
        """
        try:
            project = project_key or self.project_key
            
            payload = {
                "title": title,
                "description": description,
                "fromRef": {
                    "id": f"refs/heads/{source_branch}",
                    "repository": {
                        "slug": repo_slug,
                        "project": {
                            "key": project
                        }
                    }
                },
                "toRef": {
                    "id": f"refs/heads/{destination_branch}",
                    "repository": {
                        "slug": repo_slug,
                        "project": {
                            "key": project
                        }
                    }
                }
            }
            
            # Add reviewers if provided
            if reviewers:
                payload["reviewers"] = [{"user": {"name": reviewer}} for reviewer in reviewers]
            
            response = requests.post(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/pull-requests",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                error_message = f"Failed to create pull request: {response.status_code}"
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_message += f" - {error_data['errors'][0]['message']}"
                except:
                    pass
                
                return {"success": False, "error": error_message}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_commits(
        self,
        repo_slug: str,
        branch: Optional[str] = None,
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get commits in a repository
        
        Args:
            repo_slug: Repository slug
            branch: Optional branch to filter commits
            project_key: Project key
            
        Returns:
            List of commits
        """
        try:
            project = project_key or self.project_key
            
            params = {
                "limit": 100
            }
            
            if branch:
                params["until"] = f"refs/heads/{branch}"
            
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/commits",
                auth=self.auth,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Failed to get commits: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_content(
        self,
        repo_slug: str,
        file_path: str,
        ref: str = "master",
        project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get content of a file in a repository
        
        Args:
            repo_slug: Repository slug
            file_path: Path to the file
            ref: Git reference (branch, tag, or commit)
            project_key: Project key
            
        Returns:
            File content
        """
        try:
            project = project_key or self.project_key
            
            # For raw file content
            response = requests.get(
                f"{self.base_url}/rest/api/1.0/projects/{project}/repos/{repo_slug}/raw/{file_path}",
                auth=self.auth,
                headers={"Accept": "*/*"},  # Accept any content type
                params={"at": ref}
            )
            
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                
                # Detect if content is binary or text
                is_binary = False
                try:
                    content = response.text
                    
                    # If content is JSON
                    if content_type.startswith("application/json"):
                        content = json.loads(content)
                except UnicodeDecodeError:
                    content = "Binary file not shown"
                    is_binary = True
                
                return {
                    "success": True,
                    "data": {
                        "content": content,
                        "is_binary": is_binary,
                        "content_type": content_type,
                        "file_path": file_path,
                        "ref": ref
                    }
                }
            else:
                return {"success": False, "error": f"Failed to get file content: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}