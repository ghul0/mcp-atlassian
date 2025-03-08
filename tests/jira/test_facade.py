"""
Tests for the Jira Facade class.
"""
import unittest
import os

# Importuj dane testowe z zewnętrznego pliku
try:
    from tests.test_credentials import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, TEST_PROJECT_KEY, TEST_ISSUE_KEY
except ImportError:
    # Domyślne wartości, gdy plik test_credentials.py nie istnieje
    JIRA_URL = "https://example.atlassian.net"
    JIRA_USERNAME = "test@example.com"
    JIRA_API_TOKEN = "test-token"
    TEST_PROJECT_KEY = "TEST"
    TEST_ISSUE_KEY = "TEST-1"

from mcp_atlassian.jira.facade import JiraFetcher
from mcp_atlassian.jira.issues import IssueManager
from mcp_atlassian.config import JiraConfig
from mcp_atlassian.document_types import Document


class TestJiraFetcher(unittest.TestCase):
    """Tests for the JiraFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        # Get the test project key from environment variable
        # Get the test project key from environment variable or test_credentials
        self.project_key = os.environ.get("TEST_PROJECT_KEY", TEST_PROJECT_KEY)
        self.issue_key = os.environ.get("TEST_ISSUE_KEY", TEST_ISSUE_KEY)
        
        # Create config for tests
        self.config = JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN
        )
        
        # Create facade instance
        self.jira_fetcher = JiraFetcher(config=self.config)

    def test_initialization(self):
        """Test initialization of JiraFetcher."""
        # Verify that the facade has proper structure
        self.assertIsInstance(self.jira_fetcher.issues, IssueManager)
        self.assertEqual(self.jira_fetcher.config, self.config)
        self.assertIsNotNone(self.jira_fetcher.jira)
        self.assertIsNotNone(self.jira_fetcher.preprocessor)

    def test_get_issue_delegation(self):
        """Test that get_issue properly delegates to IssueManager."""
        # Get a real issue through the facade
        result = self.jira_fetcher.get_issue(self.issue_key)
        
        # Verify result
        self.assertIsInstance(result, Document)
        self.assertEqual(result.metadata["key"], self.issue_key)

    def test_create_issue_delegation(self):
        """Test that create_issue properly delegates to IssueManager."""
        # Create a test issue through the facade
        result = self.jira_fetcher.create_issue(
            project_key=self.project_key,
            summary="Test Issue via Facade",
            issue_type="Task",
            description="This is a test issue created via the facade."
        )
        
        # Verify result
        self.assertIsInstance(result, Document)
        self.assertEqual(result.metadata["title"], "Test Issue via Facade")
        self.assertEqual(result.metadata["type"], "Task")
        
        # Cleanup - delete the created issue
        new_issue_key = result.metadata["key"]
        self.jira_fetcher.delete_issue(new_issue_key)

    def test_update_issue_delegation(self):
        """Test that update_issue properly delegates to IssueManager."""
        # First create a test issue
        created_issue = self.jira_fetcher.create_issue(
            project_key=self.project_key,
            summary="Facade Issue to Update",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Update the issue through the facade
            fields = {"summary": "Updated Facade Issue"}
            result = self.jira_fetcher.update_issue(issue_key, fields)
            
            # Verify result
            self.assertIsInstance(result, Document)
            self.assertEqual(result.metadata["key"], issue_key)
            self.assertEqual(result.metadata["title"], "Updated Facade Issue")
        finally:
            # Cleanup
            self.jira_fetcher.delete_issue(issue_key)

    def test_delete_issue_delegation(self):
        """Test that delete_issue properly delegates to IssueManager."""
        # First create a test issue
        created_issue = self.jira_fetcher.create_issue(
            project_key=self.project_key,
            summary="Facade Issue to Delete",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        # Delete the issue through the facade
        result = self.jira_fetcher.delete_issue(issue_key)
        
        # Verify result
        self.assertTrue(result)

    def test_search_issues_delegation(self):
        """Test that search_issues properly delegates to IssueManager."""
        # Search for issues in the test project through the facade
        jql = f"project = {self.project_key}"
        results = self.jira_fetcher.search_issues(jql, limit=5)
        
        # Verify results
        self.assertIsInstance(results, list)
        if results:  # Only check if we have results
            self.assertIsInstance(results[0], Document)
            self.assertIn("key", results[0].metadata)

    def test_get_project_issues_delegation(self):
        """Test that get_project_issues properly delegates to IssueManager."""
        # Get project issues through the facade
        results = self.jira_fetcher.get_project_issues(self.project_key, limit=5)
        
        # Verify results
        self.assertIsInstance(results, list)
        if results:  # Only check if we have results
            self.assertIsInstance(results[0], Document)
            self.assertIn("key", results[0].metadata)

    def test_get_current_user_account_id_delegation(self):
        """Test that get_current_user_account_id properly delegates to IssueManager."""
        # Get current user account ID through the facade
        account_id = self.jira_fetcher.get_current_user_account_id()
        
        # Verify result
        self.assertIsNotNone(account_id)
        self.assertTrue(isinstance(account_id, str))
        self.assertTrue(len(account_id) > 0)

    def test_get_issue_comments_delegation(self):
        """Test that get_issue_comments properly delegates to IssueManager."""
        # Create a test issue
        created_issue = self.jira_fetcher.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Comment Delegation",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a comment through the facade
            self.jira_fetcher.add_comment(issue_key, "Test comment via facade")
            
            # Get comments through the facade
            comments = self.jira_fetcher.get_issue_comments(issue_key)
            
            # Verify results
            self.assertIsInstance(comments, list)
            self.assertGreaterEqual(len(comments), 1)
            self.assertIn("id", comments[0])
            self.assertIn("body", comments[0])
        finally:
            # Cleanup
            self.jira_fetcher.delete_issue(issue_key)

    def test_add_comment_delegation(self):
        """Test that add_comment properly delegates to IssueManager."""
        # Create a test issue
        created_issue = self.jira_fetcher.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Add Comment Delegation",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a comment through the facade
            result = self.jira_fetcher.add_comment(issue_key, "Test comment via facade API")
            
            # Verify result
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn("body", result)
        finally:
            # Cleanup
            self.jira_fetcher.delete_issue(issue_key)

    def test_helper_method_delegations(self):
        """Test that helper methods properly delegate to IssueManager."""
        # Test _clean_text method
        text = "Some text with [~user] mentions and [link|http://example.com]"
        result = self.jira_fetcher._clean_text(text)
        self.assertIsInstance(result, str)
        
        # Test _markdown_to_jira method
        markdown = "# Heading\n\n* Item 1\n* Item 2\n\n**Bold text**"
        result = self.jira_fetcher._markdown_to_jira(markdown)
        self.assertIsInstance(result, str)
        
        # Test get_jira_field_ids method
        field_ids = self.jira_fetcher.get_jira_field_ids()
        self.assertIsInstance(field_ids, dict)


if __name__ == "__main__":
    unittest.main()
