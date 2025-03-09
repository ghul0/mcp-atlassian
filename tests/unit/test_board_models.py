"""
Unit tests for the Jira Board models.
"""

import unittest
from mcp_atlassian.jira.models.board import (
    BoardLocation,
    Board,
)


class TestBoardModels(unittest.TestCase):
    """Test the Board Pydantic models."""

    def test_board_location_model(self):
        """Test the BoardLocation model."""
        # Test data
        data = {
            "projectId": 10000,
            "projectKey": "TEST",
            "projectName": "Test Project",
            "displayName": "Test Board"
        }
        
        # Create model instance
        location = BoardLocation(**data)
        
        # Assert attributes
        self.assertEqual(location.project_id, 10000)
        self.assertEqual(location.project_key, "TEST")
        self.assertEqual(location.project_name, "Test Project")
        self.assertEqual(location.display_name, "Test Board")
        
        # Test serialization with aliases
        serialized = location.model_dump(by_alias=True)
        self.assertEqual(serialized["projectId"], 10000)
        self.assertEqual(serialized["projectKey"], "TEST")
        self.assertEqual(serialized["projectName"], "Test Project")
        self.assertEqual(serialized["displayName"], "Test Board")

    def test_board_model(self):
        """Test the Board model."""
        # Test data
        data = {
            "id": 10000,
            "name": "Test Board",
            "type": "scrum",
            "filterId": 12345,
            "location": {
                "projectId": 10001,
                "projectKey": "TEST",
                "projectName": "Test Project",
                "displayName": "Test Board"
            }
        }
        
        # Create model instance
        board = Board(**data)
        
        # Assert attributes
        self.assertEqual(board.id, 10000)
        self.assertEqual(board.name, "Test Board")
        self.assertEqual(board.type, "scrum")
        self.assertEqual(board.filter_id, 12345)
        self.assertEqual(board.location.project_id, 10001)
        self.assertEqual(board.location.project_key, "TEST")
        
        # Test serialization with aliases
        serialized = board.model_dump(by_alias=True)
        self.assertEqual(serialized["id"], 10000)
        self.assertEqual(serialized["filterId"], 12345)
        self.assertEqual(serialized["location"]["projectId"], 10001)


if __name__ == "__main__":
    unittest.main()
