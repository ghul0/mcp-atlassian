"""
Jira API module.

This module provides comprehensive access to Jira REST API v3.
"""

from .facade import JiraFetcher
from .client import JiraClient
from .issues import IssueManager

__all__ = ["JiraFetcher", "JiraClient", "IssueManager"]
