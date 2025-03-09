"""
Jira API module for mcp-atlassian.

This module provides a comprehensive implementation of the Jira REST API v3.
It is organized into logical modules corresponding to different API areas.

The main entry point for external code is the JiraFetcher class, which provides
a backward-compatible interface to the underlying implementation.
"""

from .client import JiraClient
from .issues import IssueManager
from .projects import ProjectManager
from .facade import JiraFetcher
from .exceptions import (
    JiraAPIError,
    JiraAuthenticationError,
    JiraConfigurationError,
    JiraFieldError,
    JiraIssueTypeError,
    JiraPermissionError,
    JiraResourceNotFoundError,
    JiraValidationError,
    JiraWorkflowError,
)

__all__ = [
    "JiraClient",
    "IssueManager",
    "ProjectManager",
    "JiraFetcher",
    "JiraAPIError",
    "JiraAuthenticationError",
    "JiraConfigurationError",
    "JiraFieldError",
    "JiraIssueTypeError",
    "JiraPermissionError",
    "JiraResourceNotFoundError",
    "JiraValidationError",
    "JiraWorkflowError",
]
