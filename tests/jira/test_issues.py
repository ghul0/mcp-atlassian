import unittest
import os
from datetime import datetime

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

from mcp_atlassian.jira.issues import IssueManager
from mcp_atlassian.jira.exceptions import (
    JiraAPIError,
    JiraResourceNotFoundError,
    JiraWorkflowError,
    JiraFieldError,
    JiraIssueTypeError,
)
from mcp_atlassian.config import JiraConfig
from mcp_atlassian.document_types import Document


class TestIssueManager(unittest.TestCase):
    """Tests for the IssueManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Get the test project key from environment variable or test_credentials
        self.project_key = os.environ.get("TEST_PROJECT_KEY", TEST_PROJECT_KEY)
        self.issue_key = os.environ.get("TEST_ISSUE_KEY", TEST_ISSUE_KEY)
        
        # Create config for tests
        self.config = JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN
        )
        
        # Create instance of IssueManager
        self.issue_manager = IssueManager(config=self.config)

    def test_get_issue(self):
        """Test get_issue method."""
        # Get a real issue
        result = self.issue_manager.get_issue(self.issue_key)
        
        # Verify result
        self.assertIsInstance(result, Document)
        self.assertEqual(result.metadata["key"], self.issue_key)

    def test_create_issue(self):
        """Test create_issue method."""
        # Create a test issue
        result = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Test Issue Created by API Test",
            issue_type="Task",
            description="This is a test issue created by automated testing."
        )
        
        # Verify result
        self.assertIsInstance(result, Document)
        self.assertEqual(result.metadata["title"], "Test Issue Created by API Test")
        self.assertEqual(result.metadata["type"], "Task")
        
        # Cleanup - delete the created issue
        new_issue_key = result.metadata["key"]
        self.issue_manager.delete_issue(new_issue_key)

    def test_update_issue(self):
        """Test update_issue method."""
        # First create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue to Update",
            issue_type="Task",
            description="Original description"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Update the issue
            fields = {"summary": "Updated Issue Title"}
            result = self.issue_manager.update_issue(issue_key, fields)
            
            # Verify result
            self.assertIsInstance(result, Document)
            self.assertEqual(result.metadata["key"], issue_key)
            self.assertEqual(result.metadata["title"], "Updated Issue Title")
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_delete_issue(self):
        """Test delete_issue method."""
        # First create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue to Delete",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        # Delete the issue
        result = self.issue_manager.delete_issue(issue_key)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify that the issue no longer exists
        with self.assertRaises(JiraResourceNotFoundError):
            self.issue_manager.get_issue(issue_key)

    def test_search_issues(self):
        """Test search_issues method."""
        # Search for issues in the test project
        jql = f"project = {self.project_key}"
        results = self.issue_manager.search_issues(jql, limit=5)
        
        # Verify results
        self.assertIsInstance(results, list)
        if results:  # Only check if we have results
            self.assertIsInstance(results[0], Document)
            self.assertIn("key", results[0].metadata)

    def test_parse_time_spent(self):
        """Test _parse_time_spent method."""
        # Test various time formats
        self.assertEqual(self.issue_manager._parse_time_spent("1h"), 3600)
        self.assertEqual(self.issue_manager._parse_time_spent("30m"), 1800)
        self.assertEqual(self.issue_manager._parse_time_spent("1h 30m"), 5400)
        self.assertEqual(self.issue_manager._parse_time_spent("1d"), 86400)
        self.assertEqual(self.issue_manager._parse_time_spent("1w"), 604800)
        
        # Test invalid format
        with self.assertRaises(ValueError):
            self.issue_manager._parse_time_spent("invalid")
        
        # Test empty string
        with self.assertRaises(ValueError):
            self.issue_manager._parse_time_spent("")

    def test_update_issue_with_status_change(self):
        """Test update_issue method with status change."""
        # This test requires knowledge of the workflow, for now just assert it doesn't crash
        # First create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Status Change",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Get available transitions
            transitions = self.issue_manager.get_available_transitions(issue_key)
            
            # If we have transitions, try the first one
            if transitions:
                # Update status using the first available transition
                result = self.issue_manager.update_issue(
                    issue_key, 
                    {"status": transitions[0]["to_status"]}
                )
                
                # Verify result
                self.assertIsInstance(result, Document)
                self.assertEqual(result.metadata["key"], issue_key)
                self.assertEqual(result.metadata["status"], transitions[0]["to_status"])
        except Exception as e:
            self.fail(f"Status transition test failed with: {str(e)}")
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_add_comment(self):
        """Test add_comment method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Comments",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a comment
            comment_text = "This is a test comment created at " + datetime.now().isoformat()
            result = self.issue_manager.add_comment(issue_key, comment_text)
            
            # Verify result
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn("body", result)
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_get_issue_comments(self):
        """Test get_issue_comments method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Comment Retrieval",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a comment
            comment_text = "Comment for retrieval test"
            self.issue_manager.add_comment(issue_key, comment_text)
            
            # Get comments
            comments = self.issue_manager.get_issue_comments(issue_key)
            
            # Verify results
            self.assertIsInstance(comments, list)
            self.assertGreaterEqual(len(comments), 1)
            self.assertIn("id", comments[0])
            self.assertIn("body", comments[0])
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)
            
    def test_get_available_transitions(self):
        """Test get_available_transitions method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Transitions",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Get available transitions
            transitions = self.issue_manager.get_available_transitions(issue_key)
            
            # Verify results
            self.assertIsInstance(transitions, list)
            if transitions:  # Only check if we have transitions
                self.assertIn("id", transitions[0])
                self.assertIn("name", transitions[0])
                self.assertIn("to_status", transitions[0])
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_transition_issue(self):
        """Test transition_issue method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Transition API",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Get available transitions
            transitions = self.issue_manager.get_available_transitions(issue_key)
            
            # If we have transitions, try the first one
            if transitions:
                # Transition using the first available transition
                result = self.issue_manager.transition_issue(
                    issue_key, 
                    transitions[0]["id"]
                )
                
                # Verify result
                self.assertIsInstance(result, Document)
                self.assertEqual(result.metadata["key"], issue_key)
                self.assertEqual(result.metadata["status"], transitions[0]["to_status"])
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_add_worklog(self):
        """Test add_worklog method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Worklog",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a worklog
            result = self.issue_manager.add_worklog(
                issue_key=issue_key,
                time_spent="1h",
                comment="Test worklog entry"
            )
            
            # Verify result
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertEqual(result["timeSpent"], "1h")
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)

    def test_get_worklogs(self):
        """Test get_worklogs method."""
        # Create a test issue
        created_issue = self.issue_manager.create_issue(
            project_key=self.project_key,
            summary="Issue for Testing Worklog Retrieval",
            issue_type="Task"
        )
        issue_key = created_issue.metadata["key"]
        
        try:
            # Add a worklog
            self.issue_manager.add_worklog(
                issue_key=issue_key,
                time_spent="2h 30m",
                comment="Test worklog for retrieval"
            )
            
            # Get worklogs
            worklogs = self.issue_manager.get_worklogs(issue_key)
            
            # Verify results
            self.assertIsInstance(worklogs, list)
            self.assertGreaterEqual(len(worklogs), 1)
            self.assertIn("id", worklogs[0])
            self.assertIn("timeSpent", worklogs[0])
        finally:
            # Cleanup
            self.issue_manager.delete_issue(issue_key)
    

if __name__ == "__main__":
    unittest.main()
