"""
Pydantic models for Jira issues and related objects.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl


class User(BaseModel):
    """Represents a Jira user."""

    account_id: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[bool] = None


class IssueType(BaseModel):
    """Represents a Jira issue type."""

    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    icon_url: Optional[HttpUrl] = None
    subtask: Optional[bool] = False


class Status(BaseModel):
    """Represents a Jira issue status."""

    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None


class Priority(BaseModel):
    """Represents a Jira issue priority."""

    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    icon_url: Optional[HttpUrl] = None


class Project(BaseModel):
    """Represents a Jira project."""

    id: Optional[str] = None
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    lead: Optional[User] = None


class Comment(BaseModel):
    """Represents a Jira issue comment."""

    id: Optional[str] = None
    body: str
    author: Optional[User] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class Worklog(BaseModel):
    """Represents a Jira worklog entry."""

    id: Optional[str] = None
    comment: Optional[str] = None
    author: Optional[User] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    started: Optional[datetime] = None
    time_spent: Optional[str] = None
    time_spent_seconds: Optional[int] = None


class Transition(BaseModel):
    """Represents a Jira transition."""

    id: str
    name: Optional[str] = None
    to_status: Optional[str] = None


class IssueBase(BaseModel):
    """Base model for Jira issues."""

    summary: str
    description: Optional[str] = None
    issue_type: Union[str, Dict[str, str]]
    project: Union[str, Dict[str, str]]


class IssueCreate(IssueBase):
    """Model for creating a Jira issue."""

    assignee: Optional[Union[str, Dict[str, str]]] = None
    reporter: Optional[Union[str, Dict[str, str]]] = None
    priority: Optional[Union[str, Dict[str, str]]] = None
    labels: Optional[List[str]] = None
    components: Optional[List[Dict[str, str]]] = None
    due_date: Optional[str] = None
    parent: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IssueUpdate(BaseModel):
    """Model for updating a Jira issue."""

    summary: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[Union[str, Dict[str, str], None]] = None
    issue_type: Optional[Union[str, Dict[str, str]]] = None
    priority: Optional[Union[str, Dict[str, str], None]] = None
    labels: Optional[List[str]] = None
    components: Optional[List[Dict[str, str]]] = None
    due_date: Optional[str] = None
    transition_id: Optional[str] = None
    comment: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Issue(IssueBase):
    """Model representing a Jira issue."""

    id: Optional[str] = None
    key: str
    status: Optional[Status] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    assignee: Optional[User] = None
    reporter: Optional[User] = None
    priority: Optional[Priority] = None
    labels: Optional[List[str]] = None
    components: Optional[List[Dict[str, str]]] = None
    due_date: Optional[str] = None
    resolution: Optional[Dict[str, Any]] = None
    comments: Optional[List[Comment]] = None
    worklogs: Optional[List[Worklog]] = None
    parent: Optional[Dict[str, Any]] = None
    sub_tasks: Optional[List[Dict[str, Any]]] = None
    transitions: Optional[List[Transition]] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    url: Optional[HttpUrl] = None

    class Config:
        """Configuration for the Issue model."""

        arbitrary_types_allowed = True
