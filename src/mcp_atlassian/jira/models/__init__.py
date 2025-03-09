"""
Pydantic models for Jira API objects.

This module provides Pydantic models for various Jira API objects, including issues,
projects, users, workflows, and more. These models provide type hints, validation,
and serialization/deserialization functionality.
"""

from .issue import (
    User,
    IssueType,
    Status,
    Priority,
    Project,
    Comment,
    Worklog,
    Transition,
    IssueBase,
    IssueCreate,
    IssueUpdate,
    Issue,
)

from .board import (
    BoardLocation,
    BoardColumnStatus,
    BoardColumn,
    BoardConfiguration,
    QuickFilter,
    BoardReference,
    BoardCreate,
    BoardUpdate,
    Board,
)

__all__ = [
    # Issue models
    "User",
    "IssueType",
    "Status",
    "Priority",
    "Project",
    "Comment",
    "Worklog",
    "Transition",
    "IssueBase",
    "IssueCreate",
    "IssueUpdate",
    "Issue",
    
    # Board models
    "BoardLocation",
    "BoardColumnStatus",
    "BoardColumn",
    "BoardConfiguration",
    "QuickFilter",
    "BoardReference",
    "BoardCreate",
    "BoardUpdate",
    "Board",
]
