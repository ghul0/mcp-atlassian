"""
Facade class that provides backward compatibility with the old JiraFetcher API.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from ..document_types import Document
from ..config import JiraConfig
from .issues import IssueManager

# Configure logging
logger = logging.getLogger("mcp-jira")


class JiraFetcher:
    """
    Facade that integrates all Jira API functionalities.
    
    This class provides backward compatibility with the original JiraFetcher
    by delegating calls to the appropriate managers. It maintains the same
    method signatures and behaviors as the original class.
    """

    def __init__(self, config: Optional[JiraConfig] = None):
        """
        Initialize the Jira API facade.
        
        Args:
            config: Configuration for the Jira API. If None, it will be created
                   from environment variables.
        """
        # Initialize issue manager, which also handles general Jira client functionality
        self.issues = IssueManager(config=config)
        
        # Make client properties available directly on the facade
        self.jira = self.issues.jira
        self.config = self.issues.config
        self.preprocessor = self.issues.preprocessor
        
        # For compatibility with the original JiraFetcher
        self._field_ids_cache = self.issues._field_ids_cache

    def _clean_text(self, text: str) -> str:
        """Clean text content by processing user mentions and links."""
        return self.issues._clean_text(text)

    def _markdown_to_jira(self, markdown_text: str) -> str:
        """Convert Markdown syntax to Jira markup syntax."""
        return self.issues._markdown_to_jira(markdown_text)

    def _get_account_id(self, assignee: str) -> str:
        """Get account ID from email or full name."""
        return self.issues._get_account_id(assignee)

    def get_jira_field_ids(self) -> Dict[str, str]:
        """Dynamically discover Jira field IDs for this instance."""
        return self.issues.get_jira_field_ids()

    # Issue methods
    def get_issue(
        self,
        issue_key: str,
        expand: Optional[str] = None,
        comment_limit: Optional[Union[int, str]] = 10,
    ) -> Document:
        """Get a single issue with all its details."""
        return self.issues.get_issue(issue_key, expand, comment_limit)

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str,
        description: str = "",
        assignee: Optional[str] = None,
        **kwargs: Any,
    ) -> Document:
        """Create a new issue in Jira and return it as a Document."""
        return self.issues.create_issue(
            project_key, summary, issue_type, description, assignee, **kwargs
        )

    def update_issue(
        self, issue_key: str, fields: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Document:
        """Update an existing issue in Jira and return it as a Document."""
        return self.issues.update_issue(issue_key, fields, **kwargs)

    def delete_issue(self, issue_key: str) -> bool:
        """Delete an existing issue."""
        return self.issues.delete_issue(issue_key)

    def search_issues(
        self,
        jql: str,
        fields: str = "*all",
        start: int = 0,
        limit: int = 50,
        expand: Optional[str] = None,
    ) -> List[Document]:
        """Search for issues using JQL (Jira Query Language)."""
        return self.issues.search_issues(jql, fields, start, limit, expand)

    def get_project_issues(
        self, project_key: str, start: int = 0, limit: int = 50
    ) -> List[Document]:
        """Get all issues for a project."""
        return self.issues.get_project_issues(project_key, start, limit)

    def get_current_user_account_id(self) -> str:
        """Get the account ID of the current user."""
        return self.issues.get_current_user_account_id()

    # Comment methods
    def get_issue_comments(self, issue_key: str, limit: int = 50) -> List[Dict]:
        """Get comments for a specific issue."""
        return self.issues.get_issue_comments(issue_key, limit)

    def add_comment(self, issue_key: str, comment: str) -> Dict:
        """Add a comment to an issue."""
        return self.issues.add_comment(issue_key, comment)

    # Worklog methods
    def add_worklog(
        self,
        issue_key: str,
        time_spent: str,
        comment: str = None,
        started: str = None,
        original_estimate: str = None,
        remaining_estimate: str = None,
    ) -> Dict:
        """Add a worklog to an issue with optional estimate updates."""
        return self.issues.add_worklog(
            issue_key, time_spent, comment, started, original_estimate, remaining_estimate
        )

    def get_worklogs(self, issue_key: str) -> List[Dict]:
        """Get worklogs for an issue."""
        return self.issues.get_worklogs(issue_key)

    # Status transition methods
    def get_available_transitions(self, issue_key: str) -> List[Dict]:
        """Get the available status transitions for an issue."""
        return self.issues.get_available_transitions(issue_key)

    def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        fields: Optional[Dict] = None,
        comment: Optional[str] = None,
    ) -> Document:
        """Transition an issue to a new status using the appropriate workflow transition."""
        return self.issues.transition_issue(issue_key, transition_id, fields, comment)

    # Epic methods
    def link_issue_to_epic(self, issue_key: str, epic_key: str) -> Document:
        """Link an existing issue to an epic."""
        return self.issues.link_issue_to_epic(issue_key, epic_key)

    def get_epic_issues(self, epic_key: str, limit: int = 50) -> List[Document]:
        """Get all issues linked to a specific epic."""
        return self.issues.get_epic_issues(epic_key, limit)
