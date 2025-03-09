"""
Implementation of Jira Boards API operations.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from ..document_types import Document
from .client import JiraClient
from .exceptions import (
    JiraAPIError,
    JiraPermissionError,
    JiraResourceNotFoundError,
)

# Configure logging
logger = logging.getLogger("mcp-jira")


class BoardManager(JiraClient):
    """
    Manages Jira Board operations.

    This class provides methods for retrieving, creating, and managing boards
    in Jira, including operations on board elements like sprints, issues, and configurations.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the BoardManager."""
        super().__init__(*args, **kwargs)
        # Base path for Jira Agile API
        self._agile_path = "/rest/agile/1.0"

    def get_boards(
        self,
        start_at: int = 0,
        max_results: int = 50,
        type: Optional[str] = None,
        name: Optional[str] = None,
        project_key_or_id: Optional[str] = None,
        account_id: Optional[str] = None,
        filter_id: Optional[int] = None,
        order_by: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of boards in Jira.
        
        Args:
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            type: Type of board to filter (e.g., 'scrum', 'kanban')
            name: Name of board to filter
            project_key_or_id: Project key or ID to filter
            account_id: Account ID of user to filter boards by owner
            filter_id: Filter ID to filter
            order_by: Field to order the results by
            expand: Additional fields to expand in the response
            
        Returns:
            List of boards matching the criteria
        """
        try:
            url = f"{self._agile_path}/board"
            
            # Build query parameters
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            
            if type:
                params["type"] = type
            if name:
                params["name"] = name
            if project_key_or_id:
                params["projectKeyOrId"] = project_key_or_id
            if account_id:
                params["accountId"] = account_id
            if filter_id:
                params["filterId"] = filter_id
            if order_by:
                params["orderBy"] = order_by
            if expand:
                params["expand"] = expand
                
            response = self.jira.get(url, params=params)
            return response.get("values", [])
        except Exception as e:
            logger.error(f"Error retrieving boards: {str(e)}")
            self._handle_error(e, "boards")

    def get_board(
        self,
        board_id: int,
        expand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves details of a specific board.
        
        Args:
            board_id: ID of the board to retrieve
            expand: Additional fields to expand in the response
            
        Returns:
            Board details
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission to view the board
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}"
            
            params = {}
            if expand:
                params["expand"] = expand
                
            return self.jira.get(url, params=params)
        except Exception as e:
            logger.error(f"Error retrieving board {board_id}: {str(e)}")
            self._handle_error(e, "board", str(board_id))

    def get_board_configuration(self, board_id: int) -> Dict[str, Any]:
        """
        Retrieves the configuration of a specific board.
        
        Args:
            board_id: ID of the board
            
        Returns:
            Board configuration
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission to view the board
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/configuration"
            return self.jira.get(url)
        except Exception as e:
            logger.error(f"Error retrieving board configuration for board {board_id}: {str(e)}")
            self._handle_error(e, "board configuration", str(board_id))

    def get_board_issues(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        validate_query: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Retrieves issues from a board.
        
        Args:
            board_id: ID of the board
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            jql: JQL query to filter issues
            validate_query: Validation mode for JQL query (strict, warn, none)
            fields: List of fields to include in the response
            
        Returns:
            List of Document objects representing issues
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/issue"
            
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            
            if jql:
                params["jql"] = jql
            if validate_query:
                params["validateQuery"] = validate_query
            if fields:
                params["fields"] = ",".join(fields)
                
            response = self.jira.get(url, params=params)
            issues = response.get("issues", [])
            
            documents = []
            for issue in issues:
                issue_key = issue.get("key", "")
                summary = issue.get("fields", {}).get("summary", "")
                issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
                status = issue.get("fields", {}).get("status", {}).get("name", "")
                
                # Extract description - handle potential missing fields
                description = ""
                if "description" in issue.get("fields", {}):
                    if issue["fields"]["description"]:
                        if isinstance(issue["fields"]["description"], str):
                            description = issue["fields"]["description"]
                        elif isinstance(issue["fields"]["description"], dict):
                            # Handle Jira Cloud's Atlassian Document Format
                            content_items = issue["fields"]["description"].get("content", [])
                            for item in content_items:
                                if item.get("type") == "paragraph" and "content" in item:
                                    for text_item in item["content"]:
                                        if text_item.get("type") == "text":
                                            description += text_item.get("text", "")
                
                # Construct content
                content = f"{summary}\n\n{description}" if description else summary
                
                # Add metadata
                metadata = {
                    "key": issue_key,
                    "summary": summary,
                    "type": issue_type,
                    "status": status,
                    "url": f"{self.config.url}/browse/{issue_key}"
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
                
            return documents
        except Exception as e:
            logger.error(f"Error retrieving issues for board {board_id}: {str(e)}")
            self._handle_error(e, "board issues", str(board_id))

    def get_board_epics(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        done: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves epics from a board.
        
        Args:
            board_id: ID of the board
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            done: If true, will return only done epics, if false only not done epics
            
        Returns:
            List of epics
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/epic"
            
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            
            if done is not None:
                params["done"] = str(done).lower()
                
            response = self.jira.get(url, params=params)
            return response.get("values", [])
        except Exception as e:
            logger.error(f"Error retrieving epics for board {board_id}: {str(e)}")
            self._handle_error(e, "board epics", str(board_id))

    def get_board_backlog_issues(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        validate_query: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Retrieves issues from a board's backlog.
        
        Args:
            board_id: ID of the board
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            jql: JQL query to filter issues
            validate_query: Validation mode for JQL query (strict, warn, none)
            fields: List of fields to include in the response
            
        Returns:
            List of Document objects representing issues
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/backlog"
            
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            
            if jql:
                params["jql"] = jql
            if validate_query:
                params["validateQuery"] = validate_query
            if fields:
                params["fields"] = ",".join(fields)
                
            response = self.jira.get(url, params=params)
            issues = response.get("issues", [])
            
            documents = []
            for issue in issues:
                issue_key = issue.get("key", "")
                summary = issue.get("fields", {}).get("summary", "")
                issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
                status = issue.get("fields", {}).get("status", {}).get("name", "")
                
                # Extract description - handle potential missing fields
                description = ""
                if "description" in issue.get("fields", {}):
                    if issue["fields"]["description"]:
                        if isinstance(issue["fields"]["description"], str):
                            description = issue["fields"]["description"]
                        elif isinstance(issue["fields"]["description"], dict):
                            # Handle Jira Cloud's Atlassian Document Format
                            content_items = issue["fields"]["description"].get("content", [])
                            for item in content_items:
                                if item.get("type") == "paragraph" and "content" in item:
                                    for text_item in item["content"]:
                                        if text_item.get("type") == "text":
                                            description += text_item.get("text", "")
                
                # Construct content
                content = f"{summary}\n\n{description}" if description else summary
                
                # Add metadata
                metadata = {
                    "key": issue_key,
                    "summary": summary,
                    "type": issue_type,
                    "status": status,
                    "url": f"{self.config.url}/browse/{issue_key}",
                    "source": "backlog"
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
                
            return documents
        except Exception as e:
            logger.error(f"Error retrieving backlog issues for board {board_id}: {str(e)}")
            self._handle_error(e, "board backlog", str(board_id))

    def get_board_sprints(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves sprints from a board.
        
        Args:
            board_id: ID of the board
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            state: State of sprints to filter ('future', 'active', 'closed')
            
        Returns:
            List of sprints
            
        Raises:
            JiraResourceNotFoundError: If the board is not found
            JiraPermissionError: If the user lacks permission
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/sprint"
            
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            
            if state:
                params["state"] = state
                
            response = self.jira.get(url, params=params)
            return response.get("values", [])
        except Exception as e:
            logger.error(f"Error retrieving sprints for board {board_id}: {str(e)}")
            self._handle_error(e, "board sprints", str(board_id))

    def get_board_sprint_issues(
        self,
        board_id: int,
        sprint_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        validate_query: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Retrieves issues from a sprint in a board.
        
        Args:
            board_id: ID of the board
            sprint_id: ID of the sprint
            start_at: Index of first item to return (for pagination)
            max_results: Maximum number of items to return (for pagination)
            jql: JQL query to filter issues
            validate_query: Validation mode for JQL query (strict, warn, none)
            fields: List of fields to include in the response
            
        Returns:
            List of Document objects representing issues
            
        Raises:
            JiraResourceNotFoundError: If the board or sprint is not found
            JiraPermissionError: If the user lacks permission
            JiraAPIError: For other API errors
        """
        try:
            url = f"{self._agile_path}/board/{board_id}/sprint/{sprint_id}/issue"
            
            params = {
                "startAt": start_at,
                "