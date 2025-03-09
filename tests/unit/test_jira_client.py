"""
Unit tests for the JiraClient class that don't require actual API calls.
"""
import unittest
from unittest.mock import patch, MagicMock

from mcp_atlassian.jira.client import JiraClient
from mcp_atlassian.jira.exceptions import (
    JiraAuthenticationError,
    JiraPermissionError,
    JiraResourceNotFoundError,
    JiraAPIError,
    JiraConfigurationError,
)
from mcp_atlassian.config import JiraConfig


class TestJiraClientUnit(unittest.TestCase):
    """Unit tests for the JiraClient class using mocks."""

    def test_handle_error_with_status_code(self):
        """Test handling of errors with HTTP status codes."""
        with patch("atlassian.Jira") as mock_jira_class:
            # Create client with mock
            client = JiraClient(config=JiraConfig(
                url="https://example.atlassian.net",
                username="test_user",
                api_token="test_token"
            ))
            
            # Test 401 error
            error = MagicMock()
            error.status_code = 401
            error.__str__ = lambda x: "Unauthorized"
            
            with self.assertRaises(JiraAuthenticationError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test 403 error
            error.status_code = 403
            with self.assertRaises(JiraPermissionError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test 404 error
            error.status_code = 404
            with self.assertRaises(JiraResourceNotFoundError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test other error
            error.status_code = 500
            with self.assertRaises(JiraAPIError):
                client._handle_error(error, "issue", "TEST-1")

    def test_handle_error_with_message(self):
        """Test handling of errors based on error messages."""
        with patch("atlassian.Jira") as mock_jira_class:
            # Create client with mock
            client = JiraClient(config=JiraConfig(
                url="https://example.atlassian.net",
                username="test_user",
                api_token="test_token"
            ))
            
            # Test authentication error
            error = MagicMock()
            error.status_code = None
            error.__str__ = lambda x: "Authentication failed"
            
            with self.assertRaises(JiraAuthenticationError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test permission error
            error.__str__ = lambda x: "User does not have permission"
            with self.assertRaises(JiraPermissionError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test not found error
            error.__str__ = lambda x: "Issue does not exist"
            with self.assertRaises(JiraResourceNotFoundError):
                client._handle_error(error, "issue", "TEST-1")
            
            # Test generic error
            error.__str__ = lambda x: "Some other error"
            with self.assertRaises(JiraAPIError):
                client._handle_error(error, "issue", "TEST-1")

    def test_get_jira_field_ids_caching(self):
        """Test that get_jira_field_ids caches results."""
        with patch("atlassian.Jira") as mock_jira_class:
            # Create a Jira client instance with our mock
            mock_jira = MagicMock()
            mock_jira_class.return_value = mock_jira
            
            # Mock the fields list that would be returned from the API
            mock_fields = [
                {"id": "customfield_10001", "name": "Epic Link", "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}},
                {"id": "customfield_10002", "name": "Epic Name", "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-label"}},
                {"id": "customfield_10003", "name": "Sprint", "schema": {"custom": "com.pyxis.greenhopper.jira:gh-sprint"}},
                {"id": "customfield_10004", "name": "Story Points", "schema": {"custom": "com.atlassian.jira.plugin.system.customfieldtypes:float"}},
            ]
            
            # Mock the fields() method specifically
            # We need to patch the method after it's assigned to our mock_jira instance
            mock_jira.fields = MagicMock(return_value=mock_fields)
            
            # Create client
            client = JiraClient(config=JiraConfig(
                url="https://example.atlassian.net",
                username="test_user",
                api_token="test_token"
            ))
            client.jira = mock_jira  # Replace the real Jira instance with our mock
            
            # Clear any cache from initialization
            client._field_ids_cache = {}
            
            # First call should query the API
            field_ids = client.get_jira_field_ids()
            mock_jira.fields.assert_called_once()
            self.assertEqual(field_ids["epic_link"], "customfield_10001")
            self.assertEqual(field_ids["epic_name"], "customfield_10002")
            self.assertEqual(field_ids["sprint"], "customfield_10003")
            self.assertEqual(field_ids["story_points"], "customfield_10004")
            
            # Reset mock to verify second call doesn't hit the API
            mock_jira.fields.reset_mock()
            
            # Second call should use cache
            field_ids_2 = client.get_jira_field_ids()
            mock_jira.fields.assert_not_called()
            self.assertEqual(field_ids_2, field_ids)


if __name__ == "__main__":
    unittest.main()
