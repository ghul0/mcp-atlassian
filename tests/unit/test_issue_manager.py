"""
Unit tests for the IssueManager class that don't require actual API calls.
"""
import unittest
from unittest.mock import patch, MagicMock
import re

from mcp_atlassian.jira.issues import IssueManager
from mcp_atlassian.jira.exceptions import (
    JiraAPIError,
    JiraFieldError,
    JiraIssueTypeError,
    JiraResourceNotFoundError,
    JiraWorkflowError,
)
from mcp_atlassian.config import JiraConfig
from mcp_atlassian.document_types import Document


class TestIssueManagerUnit(unittest.TestCase):
    """Unit tests for the IssueManager class using mocks."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = JiraConfig(
            url="https://example.atlassian.net",
            username="test_user",
            api_token="test_token"
        )
        
        # Create patcher for Jira client
        self.jira_patcher = patch("atlassian.Jira")
        self.mock_jira = self.jira_patcher.start()
        
        # Create instance of IssueManager with mocked dependencies
        self.issue_manager = IssueManager(config=self.config)
        
        # Mock the TextPreprocessor - it's initialized in the constructor
        self.issue_manager.preprocessor = MagicMock()
        self.issue_manager.preprocessor.clean_jira_text.return_value = "Cleaned text"
        self.issue_manager.preprocessor.markdown_to_jira.return_value = "Jira markup text"

    def tearDown(self):
        """Tear down test fixtures."""
        self.jira_patcher.stop()

    def test_clean_text(self):
        """Test _clean_text method."""
        # Test with None
        self.assertEqual(self.issue_manager._clean_text(None), "")
        
        # Test with empty string
        self.assertEqual(self.issue_manager._clean_text(""), "")
        
        # Test with content
        self.assertEqual(self.issue_manager._clean_text("Test text"), "Cleaned text")
        self.issue_manager.preprocessor.clean_jira_text.assert_called_with("Test text")

    def test_markdown_to_jira(self):
        """Test _markdown_to_jira method."""
        # Test with None
        self.assertEqual(self.issue_manager._markdown_to_jira(None), "")
        
        # Test with empty string
        self.assertEqual(self.issue_manager._markdown_to_jira(""), "")
        
        # Test with content
        self.assertEqual(self.issue_manager._markdown_to_jira("# Heading"), "Jira markup text")
        self.issue_manager.preprocessor.markdown_to_jira.assert_called_with("# Heading")

    def test_parse_date(self):
        """Test _parse_date method."""
        # Test with None
        self.assertEqual(self.issue_manager._parse_date(None), "")
        
        # Test with empty string
        self.assertEqual(self.issue_manager._parse_date(""), "")
        
        # Test with +0000 format
        self.assertEqual(self.issue_manager._parse_date("2023-01-01T12:00:00.000+0000"), "2023-01-01")
        
        # Test with -0000 format
        self.assertEqual(self.issue_manager._parse_date("2023-01-01T12:00:00.000-0000"), "2023-01-01")
        
        # Test with +0900 format
        self.assertEqual(self.issue_manager._parse_date("2023-01-01T12:00:00.000+0900"), "2023-01-01")
        
        # Test with Z format
        self.assertEqual(self.issue_manager._parse_date("2023-01-01T12:00:00.000Z"), "2023-01-01")
        
        # Test with standard format
        self.assertEqual(self.issue_manager._parse_date("2023-01-01T12:00:00.000+00:00"), "2023-01-01")

    def test_get_account_id(self):
        """Test _get_account_id method."""
        # Setup mocks
        mock_jira = MagicMock()
        mock_jira.user_find_by_user_string.return_value = [{
            "accountId": "test-account-id",
            "displayName": "Test User",
            "emailAddress": "test@example.com"
        }]
        self.issue_manager.jira = mock_jira
        
        # Test with account ID format
        self.assertEqual(self.issue_manager._get_account_id("1234567890"), "1234567890")
        
        # Test with email
        self.assertEqual(self.issue_manager._get_account_id("test@example.com"), "test-account-id")
        mock_jira.user_find_by_user_string.assert_called_with(query="test@example.com")
        
        # Test with user not found
        mock_jira.user_find_by_user_string.return_value = []
        mock_jira.get_users_with_browse_permission_to_a_project.return_value = [{
            "accountId": "another-account-id",
            "displayName": "Another User"
        }]
        
        self.assertEqual(self.issue_manager._get_account_id("another@example.com"), "another-account-id")
        mock_jira.get_users_with_browse_permission_to_a_project.assert_called_with(username="another@example.com")
        
        # Test with user not found in either method
        mock_jira.get_users_with_browse_permission_to_a_project.return_value = []
        
        with self.assertRaises(ValueError):
            self.issue_manager._get_account_id("nonexistent@example.com")

    def test_parse_time_spent(self):
        """Test _parse_time_spent method."""
        # Test various time formats
        self.assertEqual(self.issue_manager._parse_time_spent("1h"), 3600)
        self.assertEqual(self.issue_manager._parse_time_spent("30m"), 1800)
        self.assertEqual(self.issue_manager._parse_time_spent("1h 30m"), 5400)
        self.assertEqual(self.issue_manager._parse_time_spent("1d"), 86400)
        self.assertEqual(self.issue_manager._parse_time_spent("1w"), 604800)
        
        # Calculate expected seconds for 1w 2d 3h 45m
        # 1w = 604800, 2d = 172800, 3h = 10800, 45m = 2700
        # Total = 604800 + 172800 + 10800 + 2700 = 791100
        self.assertEqual(self.issue_manager._parse_time_spent("1w 2d 3h 45m"), 791100)
        
        # Test invalid format
        with self.assertRaises(ValueError):
            self.issue_manager._parse_time_spent("invalid")
        
        # Test empty string
        with self.assertRaises(ValueError):
            self.issue_manager._parse_time_spent("")


    def test_get_available_transitions_with_object_to(self):
        """Test get_available_transitions with 'to' as an object."""
        # Setup mock
        transitions_data = {
            "transitions": [
                {
                    "id": "10",
                    "name": "Start Progress",
                    "to": {"name": "In Progress", "id": "3"}
                },
                {
                    "id": "11",
                    "name": "Resolve",
                    "to": {"name": "Resolved", "id": "4"}
                }
            ]
        }
        
        self.issue_manager.jira.get_issue_transitions = MagicMock(return_value=transitions_data)
        
        # Call the method
        transitions = self.issue_manager.get_available_transitions("TEST-1")
        
        # Verify results
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["id"], "10")
        self.assertEqual(transitions[0]["name"], "Start Progress")
        self.assertEqual(transitions[0]["to_status"], "In Progress")
        self.assertEqual(transitions[1]["id"], "11")
        self.assertEqual(transitions[1]["name"], "Resolve")
        self.assertEqual(transitions[1]["to_status"], "Resolved")
        
        # Verify mock call
        self.issue_manager.jira.get_issue_transitions.assert_called_once_with("TEST-1")
        
    def test_get_available_transitions_with_string_to(self):
        """Test get_available_transitions with 'to' as a string."""
        # Setup mock - simulating API returning 'to' as direct string
        transitions_data = {
            "transitions": [
                {
                    "id": "10",
                    "name": "Start Progress",
                    "to": "In Progress"
                },
                {
                    "id": "11",
                    "name": "Resolve",
                    "to": "Resolved"
                }
            ]
        }
        
        self.issue_manager.jira.get_issue_transitions = MagicMock(return_value=transitions_data)
        
        # Call the method
        transitions = self.issue_manager.get_available_transitions("TEST-1")
        
        # Verify results
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["id"], "10")
        self.assertEqual(transitions[0]["name"], "Start Progress")
        self.assertEqual(transitions[0]["to_status"], "In Progress")
        self.assertEqual(transitions[1]["id"], "11")
        self.assertEqual(transitions[1]["name"], "Resolve")
        self.assertEqual(transitions[1]["to_status"], "Resolved")
        
        # Verify mock call
        self.issue_manager.jira.get_issue_transitions.assert_called_once_with("TEST-1")
        
    def test_get_available_transitions_with_to_status_field(self):
        """Test get_available_transitions with 'to_status' field."""
        # Setup mock - simulating API returning 'to_status' field
        transitions_data = {
            "transitions": [
                {
                    "id": "10",
                    "name": "Start Progress",
                    "to_status": "In Progress"
                },
                {
                    "id": "11",
                    "name": "Resolve",
                    "to_status": "Resolved"
                }
            ]
        }
        
        self.issue_manager.jira.get_issue_transitions = MagicMock(return_value=transitions_data)
        
        # Call the method
        transitions = self.issue_manager.get_available_transitions("TEST-1")
        
        # Verify results
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["id"], "10")
        self.assertEqual(transitions[0]["name"], "Start Progress")
        self.assertEqual(transitions[0]["to_status"], "In Progress")
        self.assertEqual(transitions[1]["id"], "11")
        self.assertEqual(transitions[1]["name"], "Resolve")
        self.assertEqual(transitions[1]["to_status"], "Resolved")
        
        # Verify mock call
        self.issue_manager.jira.get_issue_transitions.assert_called_once_with("TEST-1")
    
    def test_get_available_transitions_with_list_format(self):
        """Test get_available_transitions with list format response."""
        # Setup mock - simulating API returning a list directly
        transitions_data = [
            {
                "id": "10",
                "name": "Start Progress",
                "to": {"name": "In Progress", "id": "3"}
            },
            {
                "id": "11",
                "name": "Resolve",
                "to": "Resolved"  # Mixed format - one object, one string
            }
        ]
        
        self.issue_manager.jira.get_issue_transitions = MagicMock(return_value=transitions_data)
        
        # Call the method
        transitions = self.issue_manager.get_available_transitions("TEST-1")
        
        # Verify results
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["id"], "10")
        self.assertEqual(transitions[0]["name"], "Start Progress")
        self.assertEqual(transitions[0]["to_status"], "In Progress")
        self.assertEqual(transitions[1]["id"], "11")
        self.assertEqual(transitions[1]["name"], "Resolve")
        self.assertEqual(transitions[1]["to_status"], "Resolved")
        
        # Verify mock call
        self.issue_manager.jira.get_issue_transitions.assert_called_once_with("TEST-1")

    def test_transition_issue_with_numeric_id(self):
        """Test transition_issue with numeric transition ID."""
        # Setup mocks
        self.issue_manager.jira.issue_transition = MagicMock()
        self.issue_manager.get_issue = MagicMock(return_value=Document(
            page_content="Test Issue", 
            metadata={"key": "TEST-1", "status": "In Progress"}
        ))
        
        # Call the method with numeric ID (int)
        result = self.issue_manager.transition_issue("TEST-1", 10)
        
        # Verify result
        self.assertIsInstance(result, Document)
        self.assertEqual(result.metadata["key"], "TEST-1")
        
        # Verify that transition_id was converted to string
        transition_data = self.issue_manager.jira.issue_transition.call_args[0][1]
        self.assertEqual(transition_data["transition"]["id"], "10")
        
        # Reset mock and test with numeric ID (float)
        self.issue_manager.jira.issue_transition.reset_mock()
        
        result = self.issue_manager.transition_issue("TEST-1", 10.0)
        
        # Verify transition_id was converted to string
        transition_data = self.issue_manager.jira.issue_transition.call_args[0][1]
        self.assertEqual(transition_data["transition"]["id"], "10.0")


if __name__ == "__main__":
    unittest.main()
