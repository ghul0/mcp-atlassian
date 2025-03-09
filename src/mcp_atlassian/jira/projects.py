"""
Module for interacting with Jira projects.

This module provides a ProjectManager class that handles operations related to Jira projects,
including retrieving, creating, updating and deleting projects, as well as managing project
components, versions, roles, and properties.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import ValidationError

from .client import JiraClient
from .exceptions import JiraAPIError, JiraValidationError
from .models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectComponentCreate,
    ProjectComponentUpdate,
    ProjectVersionCreate,
    ProjectVersionUpdate,
    ProjectCategoryCreate,
    ProjectCategoryUpdate,
)


class ProjectManager:
    """
    Manager class for Jira projects.
    
    This class provides methods for interacting with Jira projects, including
    retrieving, creating, updating, and deleting projects, as well as managing
    project components, versions, roles, and other related resources.
    """

    def __init__(self, client: JiraClient):
        """
        Initialize a new ProjectManager.
        
        Args:
            client: JiraClient instance for interacting with the Jira API
        """
        self.client = client

    def get_projects(
        self,
        recent: Optional[int] = None,
        expand: Optional[str] = None,
        order_by: Optional[str] = None,
        query: Optional[str] = None,
        status: Optional[List[str]] = None,
        type_key: Optional[List[str]] = None,
        category_id: Optional[int] = None,
        action: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> List[Project]:
        """
        Retrieve a list of projects from Jira.
        
        Args:
            recent: Limit results to specified number of recently viewed projects
            expand: Additional fields to expand (e.g., 'description,lead')
            order_by: Field to sort results by (e.g., 'key', 'name')
            query: Search string to filter projects by name or key
            status: List of project statuses to filter by (e.g., 'active', 'archived', 'deleted')
            type_key: List of project type keys to filter by (e.g., 'software', 'business')
            category_id: Project category ID to filter by
            action: Action used to filter projects (e.g., 'view', 'browse', 'edit')
            properties: List of properties to include in the response
            
        Returns:
            List of Project objects representing projects in Jira
        """
        params = {}
        
        if recent is not None:
            params["recent"] = recent
        if expand:
            params["expand"] = expand
        if order_by:
            params["orderBy"] = order_by
        if query:
            params["query"] = query
        if status:
            params["status"] = ",".join(status)
        if type_key:
            params["typeKey"] = ",".join(type_key)
        if category_id is not None:
            params["categoryId"] = category_id
        if action:
            params["action"] = action
        if properties:
            params["properties"] = ",".join(properties)
        
        try:
            projects_data = self.client.jira.projects(**params)
            return [Project.model_validate(p) for p in projects_data]
        except Exception as e:
            self.client._handle_error(e, "projects", "")

    def get_project(
        self,
        project_key_or_id: str,
        expand: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> Project:
        """
        Retrieve details of a specific project.
        
        Args:
            project_key_or_id: Project key or ID
            expand: Additional fields to expand (e.g., 'description,lead,issueTypes')
            properties: List of properties to include in the response
            
        Returns:
            Project object with project details
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        params = {}
        
        if expand:
            params["expand"] = expand
        if properties:
            params["properties"] = ",".join(properties)
        
        try:
            project_data = self.client.jira.project(project_key_or_id, **params)
            return Project.model_validate(project_data)
        except Exception as e:
            self.client._handle_error(e, "project", project_key_or_id)

    def get_project_components(self, project_key_or_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve components of a project.
        
        Args:
            project_key_or_id: Project key or ID
            
        Returns:
            List of components for the project
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            return self.client.jira.get_project_components(project_key_or_id)
        except Exception as e:
            self.client._handle_error(e, "project components", project_key_or_id)

    def get_project_versions(
        self, 
        project_key_or_id: str,
        expand: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve versions of a project.
        
        Args:
            project_key_or_id: Project key or ID
            expand: Additional fields to expand
            
        Returns:
            List of versions for the project
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        params = {}
        if expand:
            params["expand"] = expand
            
        try:
            return self.client.jira.get_project_versions(project_key_or_id, **params)
        except Exception as e:
            self.client._handle_error(e, "project versions", project_key_or_id)

    def get_project_roles(self, project_key_or_id: str) -> Dict[str, str]:
        """
        Retrieve roles of a project.
        
        Args:
            project_key_or_id: Project key or ID
            
        Returns:
            Dictionary of project roles
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            return self.client.jira.get_project_roles(project_key_or_id)
        except Exception as e:
            self.client._handle_error(e, "project roles", project_key_or_id)

    def get_project_role(
        self, 
        project_key_or_id: str, 
        role_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve details of a specific project role.
        
        Args:
            project_key_or_id: Project key or ID
            role_id: Role ID
            
        Returns:
            Details of the project role
            
        Raises:
            JiraResourceNotFoundError: If the project or role doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            return self.client.jira.get_project_role(project_key_or_id, role_id)
        except Exception as e:
            self.client._handle_error(e, f"project role {role_id}", project_key_or_id)

    def get_project_role_actors(
        self, 
        project_key_or_id: str, 
        role_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve actors of a project role.
        
        Args:
            project_key_or_id: Project key or ID
            role_id: Role ID
            
        Returns:
            List of actors for the project role
            
        Raises:
            JiraResourceNotFoundError: If the project or role doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            role_data = self.client.jira.get_project_role(project_key_or_id, role_id)
            return role_data.get("actors", [])
        except Exception as e:
            self.client._handle_error(e, f"project role actors {role_id}", project_key_or_id)

    def get_project_property(
        self, 
        project_key_or_id: str, 
        property_key: str
    ) -> Dict[str, Any]:
        """
        Retrieve a project property.
        
        Args:
            project_key_or_id: Project key or ID
            property_key: Property key
            
        Returns:
            Value of the project property
            
        Raises:
            JiraResourceNotFoundError: If the project or property doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            return self.client.jira.get_project_property(project_key_or_id, property_key)
        except Exception as e:
            self.client._handle_error(e, f"project property {property_key}", project_key_or_id)

    def get_project_properties(self, project_key_or_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all properties of a project.
        
        Args:
            project_key_or_id: Project key or ID
            
        Returns:
            List of project properties
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to view the project
        """
        try:
            return self.client.jira.get_project_properties(project_key_or_id)
        except Exception as e:
            self.client._handle_error(e, "project properties", project_key_or_id)

    def get_project_types(self) -> List[Dict[str, Any]]:
        """
        Retrieve available project types.
        
        Returns:
            List of project types
        """
        try:
            return self.client.jira.get_all_project_types()
        except Exception as e:
            self.client._handle_error(e, "project types", "")

    def get_project_type(self, type_key: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific project type.
        
        Args:
            type_key: Project type key (e.g., 'software', 'business')
            
        Returns:
            Details of the project type
            
        Raises:
            JiraResourceNotFoundError: If the project type doesn't exist
        """
        try:
            return self.client.jira.get_project_type_by_key(type_key)
        except Exception as e:
            self.client._handle_error(e, "project type", type_key)

    def get_project_categories(self) -> List[Dict[str, Any]]:
        """
        Retrieve project categories.
        
        Returns:
            List of project categories
        """
        try:
            return self.client.jira.get_all_project_categories()
        except Exception as e:
            self.client._handle_error(e, "project categories", "")

    def get_project_category(self, category_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific project category.
        
        Args:
            category_id: Category ID
            
        Returns:
            Details of the project category
            
        Raises:
            JiraResourceNotFoundError: If the category doesn't exist
        """
        try:
            return self.client.jira.get_project_category(category_id)
        except Exception as e:
            self.client._handle_error(e, "project category", category_id)

    def create_project(
        self,
        key: str,
        name: str,
        type_key: str,
        description: Optional[str] = None,
        lead_account_id: Optional[str] = None,
        url: Optional[str] = None,
        assignee_type: Optional[str] = None,
        avatar_id: Optional[int] = None,
        category_id: Optional[int] = None,
        permission_scheme: Optional[int] = None,
        notification_scheme: Optional[int] = None,
        workflow_scheme: Optional[int] = None,
        **kwargs: Any
    ) -> Project:
        """
        Create a new project in Jira.
        
        Args:
            key: Project key
            name: Project name
            type_key: Project type key (e.g., 'software', 'business')
            description: Project description
            lead_account_id: Project lead account ID
            url: Project URL
            assignee_type: Assignee type (e.g., 'PROJECT_LEAD', 'UNASSIGNED')
            avatar_id: Project avatar ID
            category_id: Project category ID
            permission_scheme: Permission scheme ID
            notification_scheme: Notification scheme ID
            workflow_scheme: Workflow scheme ID
            **kwargs: Additional options
            
        Returns:
            Project object representing the created project
            
        Raises:
            JiraValidationError: If the project data is invalid
            JiraPermissionError: If the user doesn't have permission to create a project
        """
        try:
            # Validate input data using Pydantic model
            project_data = ProjectCreate(
                key=key,
                name=name,
                projectTypeKey=type_key,  # Use the alias directly
                description=description,
                lead_account_id=lead_account_id,
                url=url,
                assignee_type=assignee_type,
                avatar_id=avatar_id,
                category_id=category_id,
                permission_scheme=permission_scheme,
                notification_scheme=notification_scheme,
                workflow_scheme=workflow_scheme,
                **kwargs
            ).model_dump(by_alias=True, exclude_none=True)  # Updated from dict() to model_dump()
            
            # Create project through API
            created_project = self.client.jira.create_project(**project_data)
            
            return Project.model_validate(created_project)
        except ValidationError as e:
            raise JiraValidationError(f"Invalid project data: {str(e)}")
        except Exception as e:
            self.client._handle_error(e, "project creation", key)

    def update_project(
        self,
        project_key_or_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        lead_account_id: Optional[str] = None,
        url: Optional[str] = None,
        assignee_type: Optional[str] = None,
        avatar_id: Optional[int] = None,
        category_id: Optional[int] = None,
        **kwargs: Any
    ) -> Project:
        """
        Update an existing project in Jira.
        
        Args:
            project_key_or_id: Project key or ID
            name: New project name
            description: New project description
            lead_account_id: New project lead account ID
            url: New project URL
            assignee_type: New assignee type
            avatar_id: New project avatar ID
            category_id: New project category ID
            **kwargs: Additional options
            
        Returns:
            Project object representing the updated project
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraValidationError: If the project data is invalid
            JiraPermissionError: If the user doesn't have permission to update the project
        """
        try:
            # Validate input data using Pydantic model
            project_data = ProjectUpdate(
                name=name,
                description=description,
                lead_account_id=lead_account_id,
                url=url,
                assignee_type=assignee_type,
                avatar_id=avatar_id,
                category_id=category_id,
                **kwargs
            ).model_dump(by_alias=True, exclude_none=True)
            
            # Don't send the request if there are no changes
            if not project_data:
                return self.get_project(project_key_or_id)
            
            # Update project through API
            updated_project = self.client.jira.update_project(project_key_or_id, **project_data)
            
            return Project.model_validate(updated_project)
        except ValidationError as e:
            raise JiraValidationError(f"Invalid project data: {str(e)}")
        except Exception as e:
            self.client._handle_error(e, "project update", project_key_or_id)

    def delete_project(
        self, 
        project_key_or_id: str, 
        enable_undo: bool = False
    ) -> bool:
        """
        Delete a project in Jira.
        
        Args:
            project_key_or_id: Project key or ID
            enable_undo: Whether to enable undoing the deletion
            
        Returns:
            True if the deletion was successful
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to delete the project
        """
        try:
            params = {}
            if enable_undo:
                params["enableUndo"] = "true"
                
            self.client.jira.delete_project(project_key_or_id, **params)
            return True
        except Exception as e:
            self.client._handle_error(e, "project deletion", project_key_or_id)

    def archive_project(self, project_key_or_id: str) -> bool:
        """
        Archive a project in Jira.
        
        Args:
            project_key_or_id: Project key or ID
            
        Returns:
            True if the archival was successful
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to archive the project
        """
        try:
            self.client.jira.archive_project(project_key_or_id)
            return True
        except Exception as e:
            self.client._handle_error(e, "project archival", project_key_or_id)

    def restore_project(self, project_key_or_id: str) -> bool:
        """
        Restore an archived project in Jira.
        
        Args:
            project_key_or_id: Project key or ID
            
        Returns:
            True if the restoration was successful
            
        Raises:
            JiraResourceNotFoundError: If the project doesn't exist
            JiraPermissionError: If the user doesn't have permission to restore the project
        """
        try:
            self.client.jira.restore_project(project_key_or_id)
            return True
        except Exception as e:
            self.client._handle_error(e, "project restoration", project_key_or_id)

    # Additional methods for Part 2 of the implementation will be added here later
