"""
Unit tests for the ProjectManager class that don't require actual API calls.
"""
import unittest
from unittest.mock import patch, MagicMock, call

from mcp_atlassian.jira.client import JiraClient
from mcp_atlassian.jira.projects import ProjectManager
from mcp_atlassian.jira.exceptions import (
    JiraAuthenticationError,
    JiraPermissionError,
    JiraResourceNotFoundError,
    JiraAPIError,
    JiraValidationError,
)
from mcp_atlassian.jira.models.project import Project, ProjectCreate, ProjectUpdate
from mcp_atlassian.config import JiraConfig


class TestProjectManagerUnit(unittest.TestCase):
    """Unit tests for the ProjectManager class using mocks."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the JiraClient
        self.mock_client_patcher = patch('mcp_atlassian.jira.client.JiraClient', autospec=True)
        self.mock_client_class = self.mock_client_patcher.start()
        
        # Create a mock for the Jira instance inside the client
        self.mock_jira = MagicMock()
        self.mock_client = self.mock_client_class.return_value
        self.mock_client.jira = self.mock_jira
        
        # Create a project manager with the mock client
        self.project_manager = ProjectManager(self.mock_client)
        
        # Sample project data for testing
        self.sample_project_data = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project",
            "projectTypeKey": "software",
            "style": "classic",
            "description": "This is a test project",
            "lead": {
                "accountId": "12345",
                "displayName": "Test User"
            },
            "isPrivate": False,
            "simplified": False,
            "components": [],
            "versions": []
        }

    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_client_patcher.stop()
    
    def test_get_projects(self):
        """Test retrieving projects."""
        # Setup mock
        projects_data = [self.sample_project_data]
        self.mock_jira.projects.return_value = projects_data
        
        # Call the method
        projects = self.project_manager.get_projects()
        
        # Verify
        self.mock_jira.projects.assert_called_once_with()
        self.assertEqual(len(projects), 1)
        self.assertIsInstance(projects[0], Project)
        self.assertEqual(projects[0].key, "TEST")
        self.assertEqual(projects[0].name, "Test Project")
    
    def test_get_projects_with_params(self):
        """Test retrieving projects with parameters."""
        # Setup mock
        projects_data = [self.sample_project_data]
        self.mock_jira.projects.return_value = projects_data
        
        # Call the method with params
        projects = self.project_manager.get_projects(
            recent=5,
            expand="description,lead",
            order_by="name",
            query="Test",
            status=["active"],
            type_key=["software"],
            category_id=123,
            action="view",
            properties=["key1", "key2"]
        )
        
        # Verify
        self.mock_jira.projects.assert_called_once_with(
            recent=5,
            expand="description,lead",
            orderBy="name",
            query="Test",
            status="active",
            typeKey="software",
            categoryId=123,
            action="view",
            properties="key1,key2"
        )
        self.assertEqual(len(projects), 1)
    
    def test_get_project(self):
        """Test retrieving a single project."""
        # Setup mock
        self.mock_jira.project.return_value = self.sample_project_data
        
        # Call the method
        project = self.project_manager.get_project("TEST")
        
        # Verify
        self.mock_jira.project.assert_called_once_with("TEST")
        self.assertIsInstance(project, Project)
        self.assertEqual(project.key, "TEST")
        self.assertEqual(project.name, "Test Project")
    
    def test_get_project_with_params(self):
        """Test retrieving a project with parameters."""
        # Setup mock
        self.mock_jira.project.return_value = self.sample_project_data
        
        # Call the method with params
        project = self.project_manager.get_project(
            "TEST",
            expand="description,lead",
            properties=["key1", "key2"]
        )
        
        # Verify
        self.mock_jira.project.assert_called_once_with(
            "TEST",
            expand="description,lead",
            properties="key1,key2"
        )
        self.assertIsInstance(project, Project)
    
    def test_get_project_components(self):
        """Test retrieving project components."""
        # Setup mock
        components_data = [
            {"id": "10001", "name": "Component 1"},
            {"id": "10002", "name": "Component 2"}
        ]
        self.mock_jira.get_project_components.return_value = components_data
        
        # Call the method
        components = self.project_manager.get_project_components("TEST")
        
        # Verify
        self.mock_jira.get_project_components.assert_called_once_with("TEST")
        self.assertEqual(len(components), 2)
        self.assertEqual(components[0]["name"], "Component 1")
        self.assertEqual(components[1]["name"], "Component 2")
    
    def test_get_project_versions(self):
        """Test retrieving project versions."""
        # Setup mock
        versions_data = [
            {"id": "10001", "name": "1.0.0"},
            {"id": "10002", "name": "2.0.0"}
        ]
        self.mock_jira.get_project_versions.return_value = versions_data
        
        # Call the method
        versions = self.project_manager.get_project_versions("TEST")
        
        # Verify
        self.mock_jira.get_project_versions.assert_called_once_with("TEST")
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]["name"], "1.0.0")
        self.assertEqual(versions[1]["name"], "2.0.0")
    
    def test_get_project_versions_with_expand(self):
        """Test retrieving project versions with expand parameter."""
        # Setup mock
        versions_data = [
            {"id": "10001", "name": "1.0.0"},
            {"id": "10002", "name": "2.0.0"}
        ]
        self.mock_jira.get_project_versions.return_value = versions_data
        
        # Call the method with expand
        versions = self.project_manager.get_project_versions("TEST", expand="operations")
        
        # Verify
        self.mock_jira.get_project_versions.assert_called_once_with("TEST", expand="operations")
        self.assertEqual(len(versions), 2)
    
    def test_get_project_roles(self):
        """Test retrieving project roles."""
        # Setup mock
        roles_data = {
            "Administrators": "https://example.com/jira/rest/api/2/project/TEST/role/10002",
            "Developers": "https://example.com/jira/rest/api/2/project/TEST/role/10003"
        }
        self.mock_jira.get_project_roles.return_value = roles_data
        
        # Call the method
        roles = self.project_manager.get_project_roles("TEST")
        
        # Verify
        self.mock_jira.get_project_roles.assert_called_once_with("TEST")
        self.assertEqual(len(roles), 2)
        self.assertIn("Administrators", roles)
        self.assertIn("Developers", roles)
    
    def test_get_project_role(self):
        """Test retrieving a specific project role."""
        # Setup mock
        role_data = {
            "self": "https://example.com/jira/rest/api/2/project/TEST/role/10002",
            "name": "Administrators",
            "id": 10002,
            "description": "Project administrators",
            "actors": [
                {
                    "id": 12345,
                    "displayName": "John Doe",
                    "type": "atlassian-user-role-actor",
                    "actorUser": {
                        "accountId": "12345",
                        "displayName": "John Doe"
                    }
                }
            ]
        }
        self.mock_jira.get_project_role.return_value = role_data
        
        # Call the method
        role = self.project_manager.get_project_role("TEST", "10002")
        
        # Verify
        self.mock_jira.get_project_role.assert_called_once_with("TEST", "10002")
        self.assertEqual(role["name"], "Administrators")
        self.assertEqual(len(role["actors"]), 1)
    
    def test_get_project_role_actors(self):
        """Test retrieving actors of a project role."""
        # Setup mock
        role_data = {
            "self": "https://example.com/jira/rest/api/2/project/TEST/role/10002",
            "name": "Administrators",
            "id": 10002,
            "description": "Project administrators",
            "actors": [
                {
                    "id": 12345,
                    "displayName": "John Doe",
                    "type": "atlassian-user-role-actor",
                    "actorUser": {
                        "accountId": "12345",
                        "displayName": "John Doe"
                    }
                }
            ]
        }
        self.mock_jira.get_project_role.return_value = role_data
        
        # Call the method
        actors = self.project_manager.get_project_role_actors("TEST", "10002")
        
        # Verify
        self.mock_jira.get_project_role.assert_called_once_with("TEST", "10002")
        self.assertEqual(len(actors), 1)
        self.assertEqual(actors[0]["displayName"], "John Doe")
        self.assertEqual(actors[0]["actorUser"]["accountId"], "12345")
    
    def test_create_project(self):
        """Test creating a project."""
        # Setup mock
        created_project_data = self.sample_project_data.copy()
        self.mock_jira.create_project.return_value = created_project_data
        
        # Call the method
        project = self.project_manager.create_project(
            key="TEST",
            name="Test Project",
            type_key="software",
            description="This is a test project",
            lead_account_id="12345"
        )
        
        # Verify
        self.mock_jira.create_project.assert_called_once()
        self.assertEqual(project.key, "TEST")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.description, "This is a test project")
    
    def test_update_project(self):
        """Test updating a project."""
        # Setup mock
        updated_project_data = self.sample_project_data.copy()
        updated_project_data["name"] = "Updated Test Project"
        updated_project_data["description"] = "This is an updated test project"
        self.mock_jira.update_project.return_value = updated_project_data
        
        # Call the method
        project = self.project_manager.update_project(
            "TEST",
            name="Updated Test Project",
            description="This is an updated test project"
        )
        
        # Verify
        self.mock_jira.update_project.assert_called_once_with(
            "TEST",
            name="Updated Test Project",
            description="This is an updated test project"
        )
        self.assertEqual(project.name, "Updated Test Project")
        self.assertEqual(project.description, "This is an updated test project")
    
    def test_delete_project(self):
        """Test deleting a project."""
        # Setup mock
        self.mock_jira.delete_project.return_value = None
        
        # Call the method
        result = self.project_manager.delete_project("TEST")
        
        # Verify
        self.mock_jira.delete_project.assert_called_once_with("TEST")
        self.assertTrue(result)
    
    def test_delete_project_with_undo(self):
        """Test deleting a project with undo option."""
        # Setup mock
        self.mock_jira.delete_project.return_value = None
        
        # Call the method
        result = self.project_manager.delete_project("TEST", enable_undo=True)
        
        # Verify
        self.mock_jira.delete_project.assert_called_once_with("TEST", enableUndo="true")
        self.assertTrue(result)
    
    def test_archive_project(self):
        """Test archiving a project."""
        # Setup mock
        self.mock_jira.archive_project.return_value = None
        
        # Call the method
        result = self.project_manager.archive_project("TEST")
        
        # Verify
        self.mock_jira.archive_project.assert_called_once_with("TEST")
        self.assertTrue(result)
    
    def test_restore_project(self):
        """Test restoring a project."""
        # Setup mock
        self.mock_jira.restore_project.return_value = None
        
        # Call the method
        result = self.project_manager.restore_project("TEST")
        
        # Verify
        self.mock_jira.restore_project.assert_called_once_with("TEST")
        self.assertTrue(result)
    
    def test_error_handling(self):
        """Test error handling for project operations."""
        # Setup mock to raise an error
        error = Exception("Project not found")
        self.mock_jira.project.side_effect = error
        self.mock_client._handle_error.side_effect = JiraResourceNotFoundError("Project 'TEST' not found")
        
        # Call the method and verify that the error is handled
        with self.assertRaises(JiraResourceNotFoundError):
            self.project_manager.get_project("TEST")
        
        # Verify that the error was handled correctly
        self.mock_client._handle_error.assert_called_once_with(error, "project", "TEST")


if __name__ == "__main__":
    unittest.main()
