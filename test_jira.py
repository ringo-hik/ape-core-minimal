"""
Test script for Jira Agent

This script tests the Jira agent functionality with a live Jira instance.
"""

import os
import sys
import time

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Jira agent
from src.agents.jira_agent import JiraAgent

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
                try:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                except ValueError:
                    continue

# Load environment variables
load_env_file()

# 환경 변수가 로드되었으므로 추가 설정 필요 없음

# Print Jira configuration for debugging
print("Jira Configuration:")
print(f"URL: {os.environ.get('APE_JIRA_URL')}")
print(f"Username: {os.environ.get('APE_JIRA_USERNAME')}")
print(f"Project Key: {os.environ.get('APE_JIRA_PROJECT_KEY')}")
print(f"API Token: {os.environ.get('APE_JIRA_API_TOKEN')[:10]}...")  # Show only first 10 chars for security

def test_jira_agent():
    """Test the Jira agent"""
    print("\nTesting Jira agent...")
    
    # Initialize Jira agent
    jira_agent = JiraAgent()
    
    # Step 1: Test authentication
    print("\nStep 1: Testing authentication...")
    auth_result = jira_agent.authenticate()
    print(f"Authentication {'successful' if auth_result else 'failed'}")
    
    if not auth_result:
        print("Authentication failed. Please check your Jira credentials.")
        return
    
    # Step 2: Get service info
    print("\nStep 2: Getting Jira service info...")
    service_info = jira_agent.get_service_info()
    
    if service_info["success"]:
        print("Service Info:")
        info = service_info["data"]
        print(f"- Base URL: {info.get('baseUrl')}")
        print(f"- Version: {info.get('version')}")
        print(f"- Build Number: {info.get('buildNumber')}")
    else:
        print(f"Failed to get service info: {service_info.get('error')}")
    
    # Step 3: Get all projects
    print("\nStep 3: Getting all available projects...")
    projects = jira_agent.get_projects()
    
    if projects["success"]:
        print("Available Projects:")
        for project in projects["data"]:
            print(f"- {project.get('name')} (Key: {project.get('key')})")
        
        # 프로젝트가 있으면 첫 번째 프로젝트 키를 사용
        if projects["data"]:
            first_project = projects["data"][0]
            jira_agent.project_key = first_project.get("key")
            print(f"\nUsing project: {first_project.get('name')} (Key: {jira_agent.project_key})")
    else:
        print(f"Failed to get projects: {projects.get('error')}")
    
    # Step 4: Get issue types
    print("\nStep 4: Getting available issue types...")
    issue_types = jira_agent.get_issue_types()
    
    if issue_types["success"]:
        print("Available Issue Types:")
        for issue_type in issue_types["data"]:
            print(f"- {issue_type.get('name')} ({issue_type.get('id')})")
    else:
        print(f"Failed to get issue types: {issue_types.get('error')}")
    
    # Step 5: Create a test issue
    print("\nStep 5: Creating a test issue...")
    timestamp = int(time.time())
    
    # 이슈 유형 ID 직접 사용
    create_result = jira_agent.process({
        "action": "create_issue",
        "summary": f"테스트 이슈 {timestamp}",
        "description": "APE Core Jira Agent로 생성된 테스트 이슈입니다.",
        "fields": {
            "project": {
                "key": jira_agent.project_key
            },
            "summary": f"테스트 이슈 {timestamp}",
            "description": "APE Core Jira Agent로 생성된 테스트 이슈입니다.",
            "issuetype": {
                "id": "10001"  # '작업' 유형의 ID
            }
        }
    })
    
    if create_result["success"]:
        issue_key = create_result["data"].get("key")
        print(f"Created issue: {issue_key}")
        
        # Step 6: Get the created issue
        print("\nStep 6: Getting the created issue details...")
        issue_details = jira_agent.get_issue(issue_key)
        
        if issue_details["success"]:
            print("Issue Details:")
            fields = issue_details["data"].get("fields", {})
            print(f"- Summary: {fields.get('summary')}")
            print(f"- Status: {fields.get('status', {}).get('name')}")
            print(f"- Created: {fields.get('created')}")
        else:
            print(f"Failed to get issue details: {issue_details.get('error')}")
        
        # Step 7: Add a comment to the issue
        print("\nStep 7: Adding a comment to the issue...")
        comment_result = jira_agent.add_comment(
            issue_key=issue_key,
            comment="This is a test comment added by the APE Core Jira Agent"
        )
        
        if comment_result["success"]:
            print("Comment added successfully")
            print(f"Comment ID: {comment_result['data'].get('id')}")
        else:
            print(f"Failed to add comment: {comment_result.get('error')}")
        
        # Step 8: Update the issue
        print("\nStep 8: Updating the issue...")
        update_result = jira_agent.update_issue(
            issue_key=issue_key,
            fields={
                "summary": f"Updated Test Issue {timestamp}",
                "description": "This issue was updated by the APE Core Jira Agent"
            }
        )
        
        if update_result["success"]:
            print("Issue updated successfully")
        else:
            print(f"Failed to update issue: {update_result.get('error')}")
        
        # Step 9: Search for issues
        print("\nStep 9: Searching for issues...")
        search_result = jira_agent.search_issues(
            jql=f"project = {jira_agent.project_key} AND summary ~ 'Test Issue'",
            max_results=10
        )
        
        if search_result["success"]:
            issues = search_result["data"].get("issues", [])
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"- {issue.get('key')}: {issue.get('fields', {}).get('summary')}")
        else:
            print(f"Failed to search issues: {search_result.get('error')}")
        
        # Optional Step 10: Delete the test issue
        # Uncomment this section if you want to delete the test issue
        """
        print("\nStep 10: Deleting the test issue...")
        delete_result = jira_agent.delete_resource("issue", issue_key)
        
        if delete_result:
            print("Issue deleted successfully")
        else:
            print("Failed to delete issue")
        """
    else:
        print(f"Failed to create issue: {create_result.get('error')}")

if __name__ == "__main__":
    test_jira_agent()