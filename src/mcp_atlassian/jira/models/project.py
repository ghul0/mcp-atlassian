"""
Pydantic models for Jira projects and related objects.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl


class ProjectTypeReference(BaseModel):
    """Reference to a project type."""
    
    key: str = Field(..., description="Project type key")
    name: str = Field(..., description="Project type name")
    description: Optional[str] = Field(None, description="Project type description")


class ProjectCategoryReference(BaseModel):
    """Reference to a project category."""
    
    id: str = Field(..., description="Project category ID")
    name: str = Field(..., description="Project category name")
    description: Optional[str] = Field(None, description="Project category description")


class ProjectLeadReference(BaseModel):
    """Reference to a project lead."""
    
    account_id: str = Field(..., description="Project lead account ID", alias="accountId")
    display_name: str = Field(..., description="Project lead display name", alias="displayName")
    email_address: Optional[str] = Field(None, description="Project lead email address", alias="emailAddress")
    active: Optional[bool] = Field(None, description="Whether the project lead is active")
    
    class Config:
        allow_population_by_field_name = True


class ProjectComponentReference(BaseModel):
    """Reference to a project component."""
    
    id: str = Field(..., description="Component ID")
    name: str = Field(..., description="Component name")
    description: Optional[str] = Field(None, description="Component description")
    lead: Optional[ProjectLeadReference] = Field(None, description="Component lead")
    assignee_type: Optional[str] = Field(None, description="Component assignee type", alias="assigneeType")
    
    class Config:
        allow_population_by_field_name = True


class ProjectVersionReference(BaseModel):
    """Reference to a project version."""
    
    id: str = Field(..., description="Version ID")
    name: str = Field(..., description="Version name")
    description: Optional[str] = Field(None, description="Version description")
    released: bool = Field(False, description="Whether the version is released")
    archived: bool = Field(False, description="Whether the version is archived")
    release_date: Optional[str] = Field(None, description="Version release date", alias="releaseDate")
    start_date: Optional[str] = Field(None, description="Version start date", alias="startDate")
    
    class Config:
        allow_population_by_field_name = True


class ProjectRoleReference(BaseModel):
    """Reference to a project role."""
    
    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")


class ProjectComponentCreate(BaseModel):
    """Data needed to create a project component."""
    
    name: str = Field(..., description="Component name")
    description: Optional[str] = Field(None, description="Component description")
    lead_account_id: Optional[str] = Field(None, description="Lead account ID", alias="leadAccountId")
    assignee_type: Optional[str] = Field(None, description="Assignee type", alias="assigneeType")
    project: str = Field(..., description="Project key or ID")
    
    class Config:
        allow_population_by_field_name = True


class ProjectComponentUpdate(BaseModel):
    """Data needed to update a project component."""
    
    name: Optional[str] = Field(None, description="New component name")
    description: Optional[str] = Field(None, description="New component description")
    lead_account_id: Optional[str] = Field(None, description="New lead account ID", alias="leadAccountId")
    assignee_type: Optional[str] = Field(None, description="New assignee type", alias="assigneeType")
    
    class Config:
        allow_population_by_field_name = True


class ProjectVersionCreate(BaseModel):
    """Data needed to create a project version."""
    
    name: str = Field(..., description="Version name")
    description: Optional[str] = Field(None, description="Version description")
    project: str = Field(..., description="Project key or ID")
    release_date: Optional[str] = Field(None, description="Release date", alias="releaseDate")
    start_date: Optional[str] = Field(None, description="Start date", alias="startDate")
    released: bool = Field(False, description="Whether the version is released")
    archived: bool = Field(False, description="Whether the version is archived")
    
    class Config:
        allow_population_by_field_name = True


class ProjectVersionUpdate(BaseModel):
    """Data needed to update a project version."""
    
    name: Optional[str] = Field(None, description="New version name")
    description: Optional[str] = Field(None, description="New version description")
    release_date: Optional[str] = Field(None, description="New release date", alias="releaseDate")
    start_date: Optional[str] = Field(None, description="New start date", alias="startDate")
    released: Optional[bool] = Field(None, description="Whether the version is released")
    archived: Optional[bool] = Field(None, description="Whether the version is archived")
    
    class Config:
        allow_population_by_field_name = True


class ProjectCreate(BaseModel):
    """Data needed to create a project."""
    
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    project_type_key: str = Field(..., description="Project type key", alias="projectTypeKey")
    description: Optional[str] = Field(None, description="Project description")
    lead_account_id: Optional[str] = Field(None, description="Lead account ID", alias="leadAccountId")
    url: Optional[str] = Field(None, description="Project URL")
    assignee_type: Optional[str] = Field(None, description="Assignee type", alias="assigneeType")
    avatar_id: Optional[int] = Field(None, description="Avatar ID", alias="avatarId")
    category_id: Optional[int] = Field(None, description="Category ID", alias="categoryId")
    permission_scheme: Optional[int] = Field(None, description="Permission scheme ID", alias="permissionScheme")
    notification_scheme: Optional[int] = Field(None, description="Notification scheme ID", alias="notificationScheme")
    workflow_scheme: Optional[int] = Field(None, description="Workflow scheme ID", alias="workflowScheme")
    
    class Config:
        allow_population_by_field_name = True


class ProjectUpdate(BaseModel):
    """Data needed to update a project."""
    
    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    lead_account_id: Optional[str] = Field(None, description="Lead account ID", alias="leadAccountId")
    url: Optional[str] = Field(None, description="Project URL")
    assignee_type: Optional[str] = Field(None, description="Assignee type", alias="assigneeType")
    avatar_id: Optional[int] = Field(None, description="Avatar ID", alias="avatarId")
    category_id: Optional[int] = Field(None, description="Category ID", alias="categoryId")
    
    class Config:
        allow_population_by_field_name = True


class ProjectCategoryCreate(BaseModel):
    """Data needed to create a project category."""
    
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class ProjectCategoryUpdate(BaseModel):
    """Data needed to update a project category."""
    
    name: Optional[str] = Field(None, description="New category name")
    description: Optional[str] = Field(None, description="New category description")


class Project(BaseModel):
    """Full project data."""
    
    id: str = Field(..., description="Project ID")
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    url: Optional[str] = Field(None, description="Project URL")
    project_type_key: str = Field(..., description="Project type key", alias="projectTypeKey")
    project_type: Optional[ProjectTypeReference] = Field(None, description="Project type reference", alias="projectType")
    simplified: bool = Field(False, description="Whether the project is simplified")
    style: str = Field(..., description="Project style")
    is_private: bool = Field(False, description="Whether the project is private", alias="isPrivate")
    lead: Optional[ProjectLeadReference] = Field(None, description="Project lead")
    components: List[ProjectComponentReference] = Field([], description="Project components")
    versions: List[ProjectVersionReference] = Field([], description="Project versions")
    category: Optional[ProjectCategoryReference] = Field(None, description="Project category")
    properties: Optional[Dict[str, Any]] = Field(None, description="Project properties")
    
    class Config:
        allow_population_by_field_name = True
