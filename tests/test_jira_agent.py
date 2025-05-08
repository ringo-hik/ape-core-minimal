"""
Unit tests for Jira Agent

This module contains unit tests for the Jira Agent.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to test
from src.agents.jira_agent import JiraAgent


class TestJiraAgent(unittest.TestCase):
    """Tests for the JiraAgent class"""
    
    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["APE_JIRA_URL"] = "https://test-jira.com"
        os.environ["APE_JIRA_API_TOKEN"] = "test-api-token"
        os.environ["APE_JIRA_USERNAME"] = "test-user@example.com"
        os.environ["APE_JIRA_PROJECT_KEY"] = "TEST"
        
        # Initialize agent
        self.jira_agent = JiraAgent()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test environment variables
        if "APE_JIRA_URL" in os.environ:
            del os.environ["APE_JIRA_URL"]
        if "APE_JIRA_API_TOKEN" in os.environ:
            del os.environ["APE_JIRA_API_TOKEN"]
        if "APE_JIRA_USERNAME" in os.environ:
            del os.environ["APE_JIRA_USERNAME"]
        if "APE_JIRA_PROJECT_KEY" in os.environ:
            del os.environ["APE_JIRA_PROJECT_KEY"]
    
    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.jira_agent.base_url, "https://test-jira.com")
        self.assertEqual(self.jira_agent.api_token, "test-api-token")
        self.assertEqual(self.jira_agent.username, "test-user@example.com")
        self.assertEqual(self.jira_agent.project_key, "TEST")
        self.assertEqual(self.jira_agent.auth, ("test-user@example.com", "test-api-token"))
        self.assertEqual(self.jira_agent.headers["Content-Type"], "application/json")
        self.assertEqual(self.jira_agent.headers["Accept"], "application/json")
    
    def test_get_capabilities(self):
        """Test getting capabilities"""
        capabilities = self.jira_agent.get_capabilities()
        self.assertEqual(len(capabilities), 7)
        self.assertIn("get_issue", capabilities)
        self.assertIn("create_issue", capabilities)
        self.assertIn("update_issue", capabilities)
        self.assertIn("search_issues", capabilities)
        self.assertIn("add_comment", capabilities)
        self.assertIn("get_projects", capabilities)
        self.assertIn("get_issue_types", capabilities)
    
    def test_validate_request_valid(self):
        """Test request validation with valid request"""
        # Valid request
        request = {"action": "get_issue", "issue_key": "TEST-123"}
        
        # Validate
        self.assertTrue(self.jira_agent.validate_request(request))
    
    def test_validate_request_invalid(self):
        """Test request validation with invalid requests"""
        # Invalid request: not a dict
        request = "not a dict"
        self.assertFalse(self.jira_agent.validate_request(request))
        
        # Invalid request: no action
        request = {"no_action": "value"}
        self.assertFalse(self.jira_agent.validate_request(request))
        
        # Invalid request: invalid action
        request = {"action": "invalid_action"}
        self.assertFalse(self.jira_agent.validate_request(request))
    
    @patch('requests.get')
    def test_authenticate_success(self, mock_get):
        """Test authentication success"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test authentication
        result = self.jira_agent.authenticate()
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/myself",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_authenticate_failure(self, mock_get):
        """Test authentication failure"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        # Test authentication
        result = self.jira_agent.authenticate()
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/myself",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_get_service_info(self, mock_get):
        """Test getting service info"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "9.0.0", "baseUrl": "https://test-jira.com"}
        mock_get.return_value = mock_response
        
        # Test get service info
        result = self.jira_agent.get_service_info()
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/serverInfo",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["version"], "9.0.0")
        self.assertEqual(result["data"]["baseUrl"], "https://test-jira.com")
    
    @patch('requests.get')
    def test_get_issue(self, mock_get):
        """Test getting issue"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue",
                "description": "This is a test issue"
            }
        }
        mock_get.return_value = mock_response
        
        # Test get issue
        result = self.jira_agent.get_issue("TEST-123")
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/issue/TEST-123",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["key"], "TEST-123")
        self.assertEqual(result["data"]["fields"]["summary"], "Test Issue")
    
    @patch('requests.post')
    def test_create_issue_with_fields(self, mock_post):
        """Test creating issue with fields"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "TEST-456", "id": "10001"}
        mock_post.return_value = mock_response
        
        # Fields for the issue
        fields = {
            "project": {"key": "TEST"},
            "summary": "New Test Issue",
            "description": "This is a new test issue",
            "issuetype": {"id": "10001"}
        }
        
        # Test create issue
        result = self.jira_agent.create_issue_with_fields(fields)
        
        # Verify
        mock_post.assert_called_with(
            "https://test-jira.com/rest/api/2/issue",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers,
            data='{"fields": {"project": {"key": "TEST"}, "summary": "New Test Issue", "description": "This is a new test issue", "issuetype": {"id": "10001"}}}'
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["key"], "TEST-456")
    
    @patch('requests.post')
    def test_create_issue(self, mock_post):
        """Test creating issue with individual parameters"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "TEST-789", "id": "10002"}
        mock_post.return_value = mock_response
        
        # Test create issue
        result = self.jira_agent.create_issue(
            "Test Summary", 
            "Test Description", 
            "Task", 
            "Medium", 
            ["label1", "label2"],
            ["component1"]
        )
        
        # Verify
        mock_post.assert_called_once()
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["key"], "TEST-789")
        
        # Verify request payload
        payload = mock_post.call_args.kwargs['data']
        self.assertIn("Test Summary", payload)
        self.assertIn("Test Description", payload)
        self.assertIn("Task", payload)
        self.assertIn("Medium", payload)
        self.assertIn("label1", payload)
        self.assertIn("component1", payload)
    
    @patch('requests.put')
    def test_update_issue(self, mock_put):
        """Test updating issue"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response
        
        # Fields to update
        fields = {
            "summary": "Updated Summary",
            "description": "Updated Description"
        }
        
        # Test update issue
        result = self.jira_agent.update_issue("TEST-123", fields)
        
        # Verify
        mock_put.assert_called_with(
            "https://test-jira.com/rest/api/2/issue/TEST-123",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers,
            data='{"fields": {"summary": "Updated Summary", "description": "Updated Description"}}'
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["issue_key"], "TEST-123")
    
    @patch('requests.post')
    def test_search_issues(self, mock_post):
        """Test searching issues"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {"key": "TEST-1", "fields": {"summary": "Issue 1"}},
                {"key": "TEST-2", "fields": {"summary": "Issue 2"}}
            ],
            "total": 2
        }
        mock_post.return_value = mock_response
        
        # Test search issues
        result = self.jira_agent.search_issues("project = TEST", 10, 0)
        
        # Verify
        mock_post.assert_called_with(
            "https://test-jira.com/rest/api/2/search",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers,
            data='{"jql": "project = TEST", "maxResults": 10, "startAt": 0, "fields": ["summary", "description", "status", "priority", "assignee"]}'
        )
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["issues"]), 2)
        self.assertEqual(result["data"]["issues"][0]["key"], "TEST-1")
        self.assertEqual(result["data"]["issues"][1]["key"], "TEST-2")
    
    @patch('requests.post')
    def test_add_comment(self, mock_post):
        """Test adding comment"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "10001", "body": "Test Comment"}
        mock_post.return_value = mock_response
        
        # Test add comment
        result = self.jira_agent.add_comment("TEST-123", "Test Comment")
        
        # Verify
        mock_post.assert_called_with(
            "https://test-jira.com/rest/api/2/issue/TEST-123/comment",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers,
            data='{"body": "Test Comment"}'
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], "10001")
        self.assertEqual(result["data"]["body"], "Test Comment")
    
    @patch('requests.get')
    def test_get_projects(self, mock_get):
        """Test getting projects"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"key": "TEST", "name": "Test Project"},
            {"key": "DEMO", "name": "Demo Project"}
        ]
        mock_get.return_value = mock_response
        
        # Test get projects
        result = self.jira_agent.get_projects()
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/project",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["key"], "TEST")
        self.assertEqual(result["data"][1]["key"], "DEMO")
    
    @patch('requests.get')
    def test_get_issue_types(self, mock_get):
        """Test getting issue types"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "10001", "name": "Task"},
            {"id": "10002", "name": "Bug"},
            {"id": "10003", "name": "Story"}
        ]
        mock_get.return_value = mock_response
        
        # Test get issue types
        result = self.jira_agent.get_issue_types()
        
        # Verify
        mock_get.assert_called_with(
            "https://test-jira.com/rest/api/2/issuetype",
            auth=self.jira_agent.auth,
            headers=self.jira_agent.headers
        )
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 3)
        self.assertEqual(result["data"][0]["name"], "Task")
        self.assertEqual(result["data"][1]["name"], "Bug")
        self.assertEqual(result["data"][2]["name"], "Story")


if __name__ == '__main__':
    unittest.main()