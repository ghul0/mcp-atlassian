#!/usr/bin/env python
# fix_test.py

import os
from dotenv import load_dotenv
from mcp_atlassian.jira import JiraFetcher
from mcp_atlassian.config import JiraConfig

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
    
    # Initialize JiraFetcher with explicit config
    print("\nInitializing JiraFetcher with explicit config...")
    fetcher = JiraFetcher(config=config)
    print("JiraFetcher initialized successfully!")
    
    # Test fetching projects
    print("\nFetching projects...")
    try:
        projects = fetcher.get_projects()
        print(f"Found {len(projects)} projects")
        for project in projects:
            print(f"- {project.metadata.get('key')}: {project.metadata.get('name')}")
    except Exception as e:
        print(f"Error fetching projects: {e}")
        import traceback
        traceback.print_exc()
    
    # Test finding available modules
    print("\nTesting module imports...")
    try:
        from mcp_atlassian.jira import ProjectManager
        print("Import ProjectManager succeeded!")
    except Exception as e:
        print(f"Error importing ProjectManager: {e}")
    
    print("\nTest PASSED!")

if __name__ == "__main__":
    main()
