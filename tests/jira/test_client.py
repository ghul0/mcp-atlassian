"""
Tests for the Jira Client base class.
"""
import os
import unittest
from unittest.mock import patch, MagicMock

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

from mcp_atlassian.jira.client import JiraClient
from mcp_atlassian.jira.exceptions import (
    JiraConfigurationError,
    JiraAuthenticationError,
    JiraResourceNotFoundError,
)
from mcp_atlassian.config import JiraConfig


class TestJiraClient(unittest.TestCase):
    """Tests for the JiraClient class."""

    @patch.dict(os.environ, {
        "JIRA_URL": "https://example.atlassian.net",
        "JIRA_USERNAME": "test_user",
        "JIRA_API_TOKEN": "test_token"
    })
    def test_create_config_from_env_cloud(self):
        """Test creating config from environment variables for cloud instance."""
        client = JiraClient()
        self.assertEqual(client.config.url, "https://example.atlassian.net")
        self.assertEqual(client.config.username, "test_user")
        self.assertEqual(client.config.api_token, "test_token")
        self.assertEqual(client.config.personal_token, "")
        self.assertTrue(client.config.verify_ssl)

    @patch.dict(os.environ, {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_PERSONAL_TOKEN": "test_personal_token"
    })
    def test_create_config_from_env_server(self):
        """Test creating config from environment variables for server instance."""
        client = JiraClient()
        self.assertEqual(client.config.url, "https://jira.example.com")
        self.assertEqual(client.config.username, "")
        self.assertEqual(client.config.api_token, "")
        self.assertEqual(client.config.personal_token, "test_personal_token")
        self.assertTrue(client.config.verify_ssl)

    @patch.dict(os.environ, {"JIRA_URL": ""})
    def test_missing_url(self):
        """Test that JiraConfigurationError is raised when URL is missing."""
        with self.assertRaises(JiraConfigurationError):
            JiraClient()

    @patch.dict(os.environ, {
        "JIRA_URL": "https://example.atlassian.net",
        "JIRA_USERNAME": "",
        "JIRA_API_TOKEN": ""
    })
    def test_missing_cloud_credentials(self):
        """Test that JiraConfigurationError is raised when cloud credentials are missing."""
        with self.assertRaises(JiraConfigurationError):
            JiraClient()

    @patch.dict(os.environ, {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_PERSONAL_TOKEN": ""
    })
    def test_missing_server_credentials(self):
        """Test that JiraConfigurationError is raised when server credentials are missing."""
        with self.assertRaises(JiraConfigurationError):
            JiraClient()

    def test_init_with_provided_config(self):
        """Test initialization with provided config."""
        config = JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN,
            personal_token="",
            verify_ssl=True
        )
        client = JiraClient(config=config)
        self.assertEqual(client.config, config)
        
        # Verify that connection works by getting account ID
        account_id = client.get_current_user_account_id()
        self.assertIsInstance(account_id, str)
        self.assertTrue(len(account_id) > 0)

    def test_handle_error_authentication(self):
        """Test that handle_error correctly handles authentication errors."""
        client = JiraClient(config=JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN
        ))
        
        # Create a mock error with status_code attribute
        error = MagicMock()
        error.status_code = 401
        error.__str__ = lambda x: "Unauthorized"
        
        with self.assertRaises(JiraAuthenticationError):
            client._handle_error(error, "issue", TEST_ISSUE_KEY)

    def test_handle_error_not_found(self):
        """Test that handle_error correctly handles resource not found errors."""
        client = JiraClient(config=JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN
        ))
        
        # Create a mock error with status_code attribute
        error = MagicMock()
        error.status_code = 404
        error.__str__ = lambda x: "Not Found"
        
        with self.assertRaises(JiraResourceNotFoundError):
            client._handle_error(error, "issue", f"{TEST_PROJECT_KEY}-999")

    def test_get_current_user_account_id(self):
        """Test getting current user's account ID."""
        # Create client with valid credentials
        client = JiraClient(config=JiraConfig(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            api_token=JIRA_API_TOKEN
        ))
        
        # Test the method with real API call
        account_id = client.get_current_user_account_id()
        self.assertIsNotNone(account_id)
        self.assertTrue(isinstance(account_id, str))


if __name__ == "__main__":
    unittest.main()
