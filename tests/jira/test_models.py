"""
Tests for the Jira API models.
"""
import unittest
from datetime import datetime
from typing import Dict, Any

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

from mcp_atlassian.jira.models.issue import (
    User,
    IssueType,
    Status,
    Priority,
    Project,
    Comment,
    Worklog,
    Transition,
    IssueCreate,
    IssueUpdate,
    Issue,
)
from pydantic import ValidationError


class TestJiraModels(unittest.TestCase):
    """Tests for Jira API models."""

    def test_user_model(self):
        """Test the User model."""
        # Test with minimum required fields (none)
        user = User()
        self.assertIsNone(user.account_id)
        self.assertIsNone(user.display_name)
        
        # Test with all fields
        user_data = {
            "account_id": "123456",
            "display_name": "Test User",
            "email": "test@example.com",
            "active": True
        }
        user = User(**user_data)
        self.assertEqual(user.account_id, "123456")
        self.assertEqual(user.display_name, "Test User")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.active)

    def test_issue_type_model(self):
        """Test the IssueType model."""
        # Test with minimum required fields
        issue_type = IssueType(name="Bug")
        self.assertEqual(issue_type.name, "Bug")
        self.assertIsNone(issue_type.id)
        
        # Test with all fields
        issue_type_data = {
            "id": "10001",
            "name": "Bug",
            "description": "A bug in the system",
            "icon_url": "https://example.com/bug.png",
            "subtask": False
        }
        issue_type = IssueType(**issue_type_data)
        self.assertEqual(issue_type.id, "10001")
        self.assertEqual(issue_type.name, "Bug")
        self.assertEqual(issue_type.description, "A bug in the system")
        self.assertEqual(str(issue_type.icon_url), "https://example.com/bug.png")
        self.assertFalse(issue_type.subtask)

    def test_status_model(self):
        """Test the Status model."""
        # Test with minimum required fields
        status = Status(name="Open")
        self.assertEqual(status.name, "Open")
        self.assertIsNone(status.id)
        
        # Test with all fields
        status_data = {
            "id": "10001",
            "name": "Open",
            "description": "Issue is open",
            "category_id": "1",
            "category_name": "To Do"
        }
        status = Status(**status_data)
        self.assertEqual(status.id, "10001")
        self.assertEqual(status.name, "Open")
        self.assertEqual(status.description, "Issue is open")
        self.assertEqual(status.category_id, "1")
        self.assertEqual(status.category_name, "To Do")

    def test_issue_create_model(self):
        """Test the IssueCreate model."""
        # Test with minimum required fields
        issue_create = IssueCreate(
            summary="Test Issue",
            issue_type="Bug",
            project="TEST"
        )
        self.assertEqual(issue_create.summary, "Test Issue")
        self.assertEqual(issue_create.issue_type, "Bug")
        self.assertEqual(issue_create.project, "TEST")
        
        # Test with issue_type as dict
        issue_create = IssueCreate(
            summary="Test Issue",
            issue_type={"name": "Bug"},
            project="TEST"
        )
        self.assertEqual(issue_create.issue_type, {"name": "Bug"})
        
        # Test with all fields
        issue_create_data: Dict[str, Any] = {
            "summary": "Test Issue",
            "description": "This is a test issue",
            "issue_type": "Bug",
            "project": TEST_PROJECT_KEY,
            "assignee": "user@example.com",
            "reporter": "reporter@example.com",
            "priority": "High",
            "labels": ["test", "bug"],
            "components": [{"name": "UI"}],
            "due_date": "2023-12-31",
            "parent": {"key": TEST_ISSUE_KEY},
            "custom_fields": {"customfield_10001": "Custom Value"}
        }
        issue_create = IssueCreate(**issue_create_data)
        self.assertEqual(issue_create.summary, "Test Issue")
        self.assertEqual(issue_create.description, "This is a test issue")
        self.assertEqual(issue_create.issue_type, "Bug")
        self.assertEqual(issue_create.project, "TEST")
        self.assertEqual(issue_create.assignee, "user@example.com")
        self.assertEqual(issue_create.labels, ["test", "bug"])
        self.assertEqual(issue_create.components, [{"name": "UI"}])
        self.assertEqual(issue_create.due_date, "2023-12-31")
        self.assertEqual(issue_create.parent, {"key": "TEST-1"})
        self.assertEqual(issue_create.custom_fields, {"customfield_10001": "Custom Value"})

    def test_issue_update_model(self):
        """Test the IssueUpdate model."""
        # Test with no fields (all optional)
        issue_update = IssueUpdate()
        self.assertIsNone(issue_update.summary)
        
        # Test with some fields
        issue_update = IssueUpdate(summary="Updated Issue")
        self.assertEqual(issue_update.summary, "Updated Issue")
        
        # Test with all fields
        issue_update_data: Dict[str, Any] = {
            "summary": "Updated Issue",
            "description": "This is an updated issue",
            "assignee": "user@example.com",
            "issue_type": "Bug",
            "priority": "High",
            "labels": ["test", "bug"],
            "components": [{"name": "UI"}],
            "due_date": "2023-12-31",
            "transition_id": "10001",
            "comment": "This is a comment",
            "custom_fields": {"customfield_10001": "Custom Value"}
        }
        issue_update = IssueUpdate(**issue_update_data)
        self.assertEqual(issue_update.summary, "Updated Issue")
        self.assertEqual(issue_update.description, "This is an updated issue")
        self.assertEqual(issue_update.assignee, "user@example.com")
        self.assertEqual(issue_update.issue_type, "Bug")
        self.assertEqual(issue_update.priority, "High")
        self.assertEqual(issue_update.labels, ["test", "bug"])
        self.assertEqual(issue_update.components, [{"name": "UI"}])
        self.assertEqual(issue_update.due_date, "2023-12-31")
        self.assertEqual(issue_update.transition_id, "10001")
        self.assertEqual(issue_update.comment, "This is a comment")
        self.assertEqual(issue_update.custom_fields, {"customfield_10001": "Custom Value"})

    def test_issue_model(self):
        """Test the Issue model."""
        # Test with minimum required fields
        issue = Issue(
            key="TEST-1",
            summary="Test Issue",
            issue_type="Bug",
            project="TEST"
        )
        self.assertEqual(issue.key, "TEST-1")
        self.assertEqual(issue.summary, "Test Issue")
        self.assertEqual(issue.issue_type, "Bug")
        self.assertEqual(issue.project, "TEST")
        
        # Test with some optional fields
        issue = Issue(
            key="TEST-1",
            summary="Test Issue",
            description="This is a test issue",
            issue_type={"name": "Bug"},
            project={"key": "TEST"},
            status=Status(name="Open"),
            created=datetime.fromisoformat("2023-01-01T12:00:00+00:00"),
            updated=datetime.fromisoformat("2023-01-02T12:00:00+00:00")
        )
        self.assertEqual(issue.key, "TEST-1")
        self.assertEqual(issue.summary, "Test Issue")
        self.assertEqual(issue.description, "This is a test issue")
        self.assertEqual(issue.issue_type, {"name": "Bug"})
        self.assertEqual(issue.project, {"key": "TEST"})
        self.assertEqual(issue.status.name, "Open")
        self.assertEqual(issue.created, datetime.fromisoformat("2023-01-01T12:00:00+00:00"))
        self.assertEqual(issue.updated, datetime.fromisoformat("2023-01-02T12:00:00+00:00"))
        
        # Test with nested models
        # We need to convert nested models to dictionaries for proper validation
        issue_type_instance = IssueType(name="Bug")
        project_instance = Project(key="TEST")
        status_instance = Status(name="Open")
        user_instance = User(display_name="Test User")
        
        issue_type_dict = issue_type_instance.model_dump()
        project_dict = project_instance.model_dump()
        status_dict = status_instance.model_dump()
        user_dict = user_instance.model_dump()
        
        issue = Issue(
            key="TEST-1",
            summary="Test Issue",
            issue_type=issue_type_dict,
            project=project_dict,
            status=status_dict,
            created=datetime.fromisoformat("2023-01-01T12:00:00+00:00"),
            assignee=user_dict,
            comments=[
                {"id": "10001", "body": "Test comment", 
                        "author": user_dict,
                        "created": datetime.fromisoformat("2023-01-01T12:00:00+00:00")}
            ],
            worklogs=[
                {"id": "10001", "comment": "Test worklog",
                        "author": user_dict,
                        "time_spent": "1h",
                        "time_spent_seconds": 3600}
            ],
            transitions=[
                {"id": "10001", "name": "Start Progress", "to_status": "In Progress"}
            ]
        )
        self.assertEqual(issue.key, "TEST-1")
        self.assertEqual(issue.issue_type["name"], "Bug")
        self.assertEqual(issue.project["key"], "TEST")
        self.assertEqual(issue.status["name"], "Open")
        self.assertEqual(issue.assignee["display_name"], "Test User")
        self.assertEqual(len(issue.comments), 1)
        self.assertEqual(issue.comments[0]["id"], "10001")
        self.assertEqual(issue.comments[0]["body"], "Test comment")
        self.assertEqual(issue.comments[0]["author"]["display_name"], "Test User")
        self.assertEqual(len(issue.worklogs), 1)
        self.assertEqual(issue.worklogs[0]["id"], "10001")
        self.assertEqual(issue.worklogs[0]["comment"], "Test worklog")
        self.assertEqual(issue.worklogs[0]["time_spent"], "1h")
        self.assertEqual(issue.worklogs[0]["time_spent_seconds"], 3600)
        self.assertEqual(len(issue.transitions), 1)
        self.assertEqual(issue.transitions[0]["id"], "10001")
        self.assertEqual(issue.transitions[0]["name"], "Start Progress")
        self.assertEqual(issue.transitions[0]["to_status"], "In Progress")


if __name__ == "__main__":
    unittest.main()
