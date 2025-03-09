"""
Unit tests for the BoardManager class that don't require actual API calls.
"""
import unittest
from unittest.mock import patch, MagicMock, call

from mcp_atlassian.jira.boards import BoardManager
from mcp_atlassian.jira.client import JiraClient
from mcp_atlassian.jira.exceptions import (
    JiraAuthenticationError,
    JiraPermissionError,
    JiraResourceNotFoundError,
    JiraAPIError,
    JiraValidationError,
)
from mcp_atlassian.config import JiraConfig


class TestBoardManagerUnit(unittest.TestCase):
    """Unit tests for the BoardManager class using mocks."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a patched configuration
        self.config = JiraConfig(
            url="https://example.atlassian.net",
            username="test_user",
            api_token="test_token"
        )
        
        # Create a mock for the Jira REST client
        self.patcher = patch('mcp_atlassian.jira.client.Jira')
        self.mock_jira_class = self.patcher.start()
        self.mock_jira = self.mock_jira_class.return_value
        
        # Create the board manager with mocked dependencies
        self.board_manager = BoardManager(self.config)
        self.board_manager.jira = self.mock_jira
        
        # Sample board data for testing
        self.sample_board_data = {
            "id": 1,
            "name": "Test Board",
            "type": "scrum",
            "location": {
                "projectKey": "TEST",
                "projectName": "Test Project",
                "displayName": "Test Project Board"
            },
            "filterId": 12345
        }
        
        # Sample response for get_boards
        self.sample_boards_response = {
            "maxResults": 50,
            "startAt": 0,
            "total": 2,
            "isLast": True,
            "values": [
                self.sample_board_data,
                {
                    "id": 2,
                    "name": "Another Board",
                    "type": "kanban",
                    "location": {
                        "projectKey": "PROJ",
                        "projectName": "Project",
                        "displayName": "Project Board"
                    },
                    "filterId": 54321
                }
            ]
        }
        
        # Sample configuration response
        self.sample_configuration = {
            "id": 1,
            "name": "Test Board",
            "columnConfig": {
                "columns": [
                    {
                        "name": "To Do",
                        "statuses": [{"id": "10000", "name": "To Do"}]
                    },
                    {
                        "name": "In Progress",
                        "statuses": [{"id": "10001", "name": "In Progress"}]
                    },
                    {
                        "name": "Done",
                        "statuses": [{"id": "10002", "name": "Done"}]
                    }
                ]
            }
        }
        
        # Sample sprint data
        self.sample_sprint = {
            "id": 123,
            "name": "Sprint 1",
            "state": "active",
            "startDate": "2023-01-01T00:00:00.000Z",
            "endDate": "2023-01-15T00:00:00.000Z"
        }
        
        # Sample issue data
        self.sample_issue = {
            "key": "TEST-1",
            "fields": {
                "summary": "Test issue",
                "description": "This is a test issue",
                "issuetype": {"name": "Story"},
                "status": {"name": "In Progress"}
            }
        }
        
        # Sample epic data
        self.sample_epic = {
            "id": 456,
            "key": "TEST-2",
            "name": "Test Epic",
            "summary": "Epic summary",
            "done": False
        }
        
        # Sample quick filter data
        self.sample_quick_filter = {
            "id": 789,
            "name": "My Issues",
            "jql": "assignee = currentUser()"
        }
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
    
    def test_get_boards(self):
        """Test retrieving boards."""
        # Configure mock
        self.mock_jira.get.return_value = self.sample_boards_response
        
        # Call the method
        result = self.board_manager.get_boards(
            start_at=0, 
            max_results=50, 
            type="scrum", 
            name="Test", 
            project_key_or_id="TEST"
        )
        
        # Assert result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "Test Board")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board",
            params={
                "startAt": 0,
                "maxResults": 50,
                "type": "scrum",
                "name": "Test",
                "projectKeyOrId": "TEST"
            }
        )
    
    def test_get_board(self):
        """Test retrieving a single board."""
        # Configure mock
        self.mock_jira.get.return_value = self.sample_board_data
        
        # Call the method
        result = self.board_manager.get_board(1)
        
        # Assert result
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Board")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1",
            params={}
        )
    
    def test_get_board_configuration(self):
        """Test retrieving a board configuration."""
        # Configure mock
        self.mock_jira.get.return_value = self.sample_configuration
        
        # Call the method
        result = self.board_manager.get_board_configuration(1)
        
        # Assert result
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Board")
        self.assertEqual(len(result["columnConfig"]["columns"]), 3)
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/configuration"
        )
    
    def test_get_board_issues(self):
        """Test retrieving issues from a board."""
        # Configure mock
        self.mock_jira.get.return_value = {"issues": [self.sample_issue]}
        
        # Call the method
        result = self.board_manager.get_board_issues(1)
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["key"], "TEST-1")
        self.assertEqual(result[0].metadata["summary"], "Test issue")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/issue",
            params={"startAt": 0, "maxResults": 50}
        )
    
    def test_get_board_epics(self):
        """Test retrieving epics from a board."""
        # Sample epics response
        sample_epics_response = {
            "maxResults": 50,
            "startAt": 0,
            "total": 1,
            "isLast": True,
            "values": [self.sample_epic]
        }
        
        # Configure mock
        self.mock_jira.get.return_value = sample_epics_response
        
        # Call the method
        result = self.board_manager.get_board_epics(1, done=False)
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 456)
        self.assertEqual(result[0]["name"], "Test Epic")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/epic",
            params={"startAt": 0, "maxResults": 50, "done": "false"}
        )
    
    def test_get_board_backlog_issues(self):
        """Test retrieving backlog issues from a board."""
        # Configure mock
        self.mock_jira.get.return_value = {"issues": [self.sample_issue]}
        
        # Call the method
        result = self.board_manager.get_board_backlog_issues(1)
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["key"], "TEST-1")
        self.assertEqual(result[0].metadata["source"], "backlog")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/backlog",
            params={"startAt": 0, "maxResults": 50}
        )
    
    def test_get_board_sprints(self):
        """Test retrieving sprints from a board."""
        # Sample sprints response
        sample_sprints_response = {
            "maxResults": 50,
            "startAt": 0,
            "total": 1,
            "isLast": True,
            "values": [self.sample_sprint]
        }
        
        # Configure mock
        self.mock_jira.get.return_value = sample_sprints_response
        
        # Call the method
        result = self.board_manager.get_board_sprints(1, state="active")
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 123)
        self.assertEqual(result[0]["name"], "Sprint 1")
        self.assertEqual(result[0]["state"], "active")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/sprint",
            params={"startAt": 0, "maxResults": 50, "state": "active"}
        )
    
    def test_get_board_sprint_issues(self):
        """Test retrieving sprint issues from a board."""
        # Configure mock
        self.mock_jira.get.return_value = {"issues": [self.sample_issue]}
        
        # Call the method
        result = self.board_manager.get_board_sprint_issues(1, 123)
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["key"], "TEST-1")
        self.assertEqual(result[0].metadata["source"], "sprint")
        self.assertEqual(result[0].metadata["sprint_id"], 123)
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/sprint/123/issue",
            params={"startAt": 0, "maxResults": 50}
        )
        
    def test_create_board(self):
        """Test creating a board."""
        # Configure mock
        self.mock_jira.post.return_value = self.sample_board_data
        
        # Call the method
        result = self.board_manager.create_board(
            name="Test Board",
            type="scrum",
            filter_id=12345,
            project_key_or_id="TEST"
        )
        
        # Assert result
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Board")
        
        # Assert mock was called correctly
        self.mock_jira.post.assert_called_once_with(
            "/rest/agile/1.0/board",
            json={
                "name": "Test Board",
                "type": "scrum",
                "filterId": 12345,
                "location": {
                    "projectKeyOrId": "TEST"
                }
            }
        )
        
    def test_update_board(self):
        """Test updating a board."""
        # Configure mock
        self.mock_jira.put.return_value = self.sample_board_data
        
        # Call the method
        result = self.board_manager.update_board(
            board_id=1,
            name="Updated Board",
            filter_id=54321
        )
        
        # Assert result
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Board")
        
        # Assert mock was called correctly
        self.mock_jira.put.assert_called_once_with(
            "/rest/agile/1.0/board/1",
            json={
                "name": "Updated Board",
                "filterId": 54321
            }
        )
        
    def test_delete_board(self):
        """Test deleting a board."""
        # Call the method
        result = self.board_manager.delete_board(1)
        
        # Assert result
        self.assertTrue(result)
        
        # Assert mock was called correctly
        self.mock_jira.delete.assert_called_once_with("/rest/agile/1.0/board/1")
        
    def test_get_board_quick_filters(self):
        """Test retrieving quick filters for a board."""
        # Sample quick filters response
        sample_quick_filters_response = {
            "maxResults": 50,
            "startAt": 0,
            "total": 1,
            "isLast": True,
            "values": [self.sample_quick_filter]
        }
        
        # Configure mock
        self.mock_jira.get.return_value = sample_quick_filters_response
        
        # Call the method
        result = self.board_manager.get_board_quick_filters(1)
        
        # Assert result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 789)
        self.assertEqual(result[0]["name"], "My Issues")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/quickfilter"
        )
        
    def test_get_board_columns(self):
        """Test retrieving columns for a board."""
        # Configure mock
        self.mock_jira.get.return_value = self.sample_configuration
        
        # Call the method
        result = self.board_manager.get_board_columns(1)
        
        # Assert result
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "To Do")
        self.assertEqual(result[1]["name"], "In Progress")
        self.assertEqual(result[2]["name"], "Done")
        
        # Assert mock was called correctly
        self.mock_jira.get.assert_called_once_with(
            "/rest/agile/1.0/board/1/configuration"
        )
        
    def test_error_handling(self):
        """Test error handling when API calls fail."""
        # Set up mock to raise exception
        self.mock_jira.get.side_effect = JiraResourceNotFoundError("Board not found", status_code=404)
        
        # Call the method and check that the exception is propagated
        with self.assertRaises(JiraResourceNotFoundError):
            self.board_manager.get_board(1)


if __name__ == "__main__":
    unittest.main()
