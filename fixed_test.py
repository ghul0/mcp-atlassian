#!/usr/bin/env python
# fixed_test.py

import os
from dotenv import load_dotenv
from mcp_atlassian.config import JiraConfig
from mcp_atlassian.jira.client import JiraClient
from mcp_atlassian.jira.issues import IssueManager
from mcp_atlassian.jira.projects import ProjectManager

def main():
    # Load environment variables
    load_dotenv()
    
    # Print environment variables for debugging
    print("Environment variables:")
    print(f"JIRA_URL: {os.getenv('JIRA_URL')}")
    print(f"JIRA_USERNAME: {os.getenv('JIRA_USERNAME')}")
    print(f"JIRA_API_TOKEN: {os.getenv('JIRA_API_TOKEN')}")
    
    # Create JiraConfig manually
    config = JiraConfig(
        url=os.getenv("JIRA_URL"),
        username=os.getenv("JIRA_USERNAME", ""),
        api_token=os.getenv("JIRA_API_TOKEN", ""),
        personal_token=os.getenv("JIRA_PERSONAL_TOKEN", ""),
        verify_ssl=os.getenv("JIRA_SSL_VERIFY", "true").lower() != "false"
    )
    
    # Initialize JiraClient directly
    print("\nInitializing JiraClient...")
    client = JiraClient(config=config)
    print("JiraClient initialized successfully!")
    
    # Initialize individual managers
    print("\nInitializing individual managers...")
    issue_manager = IssueManager(config=config)
    project_manager = ProjectManager(client)
    print("Managers initialized successfully!")
    
    # Test fetching projects
    print("\nFetching projects...")
    try:
        projects = project_manager.get_projects()
        print(f"Found {len(projects)} projects")
        for project in projects:
            print(f"- {project.metadata.get('key')}: {project.metadata.get('name')}")
    except Exception as e:
        print(f"Error fetching projects: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest PASSED!")

if __name__ == "__main__":
    main()
