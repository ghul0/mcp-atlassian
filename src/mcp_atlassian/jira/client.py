"""
Base Jira API client implementation.
"""

import os
import logging
from typing import Any, Optional, Dict, List, Union
from atlassian import Jira

from ..config import JiraConfig
from .exceptions import (
    JiraAPIError,
    JiraAuthenticationError,
    JiraPermissionError,
    JiraResourceNotFoundError,
    JiraConfigurationError,
)

# Configure logging
logger = logging.getLogger("mcp-jira")


class JiraClient:
    """Base class for Jira API client."""

    def __init__(self, config: Optional[JiraConfig] = None):
        """
        Initialize the Jira API client.

        Args:
            config: Jira configuration. If None, it will be created from environment variables.
        """
        # Initialize configuration from parameters or environment
        if config is None:
            config = self._create_config_from_env()

        self.config = config
        self._init_client()

    def _create_config_from_env(self) -> JiraConfig:
        """
        Create Jira configuration from environment variables.

        Returns:
            JiraConfig: Configuration object with values from environment variables.

        Raises:
            JiraConfigurationError: If required environment variables are missing.
        """
        url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME", "")
        token = os.getenv("JIRA_API_TOKEN", "")
        personal_token = os.getenv("JIRA_PERSONAL_TOKEN", "")
        verify_ssl = os.getenv("JIRA_SSL_VERIFY", "true").lower() != "false"

        if not url:
            raise JiraConfigurationError("Missing required JIRA_URL environment variable")

        return JiraConfig(
            url=url,
            username=username,
            api_token=token,
            personal_token=personal_token,
            verify_ssl=verify_ssl,
        )

    def _init_client(self) -> None:
        """
        Initialize the Jira client based on configuration.

        Raises:
            JiraConfigurationError: If authentication information is missing.
        """
        is_cloud = "atlassian.net" in self.config.url

        try:
            if is_cloud:
                if not self.config.username or not self.config.api_token:
                    raise JiraConfigurationError(
                        "Cloud authentication requires JIRA_USERNAME and JIRA_API_TOKEN"
                    )

                self.jira = Jira(
                    url=self.config.url,
                    username=self.config.username,
                    password=self.config.api_token,
                    cloud=True,
                    verify_ssl=self.config.verify_ssl,
                )
            else:
                if not self.config.personal_token:
                    raise JiraConfigurationError(
                        "Server/Data Center authentication requires JIRA_PERSONAL_TOKEN"
                    )

                self.jira = Jira(
                    url=self.config.url,
                    token=self.config.personal_token,
                    cloud=False,
                    verify_ssl=self.config.verify_ssl,
                )

            # Initialize field IDs cache
            self._field_ids_cache: Dict[str, str] = {}

        except Exception as e:
            logger.error(f"Error initializing Jira client: {str(e)}")
            raise JiraConfigurationError(f"Failed to initialize Jira client: {str(e)}")

    def _handle_error(self, e: Exception, resource_type: str, resource_id: str = "") -> None:
        """
        Handle API errors and raise appropriate exceptions.

        Args:
            e: The exception that occurred.
            resource_type: The type of resource being accessed (e.g., "issue", "project").
            resource_id: The ID or key of the resource being accessed.

        Raises:
            JiraAuthenticationError: For authentication errors.
            JiraPermissionError: For permission errors.
            JiraResourceNotFoundError: For resource not found errors.
            JiraAPIError: For other API errors.
        """
        error_message = str(e)
        status_code = getattr(e, "status_code", None)
        response = getattr(e, "response", None)

        if hasattr(e, "status_code"):
            if status_code == 401:
                raise JiraAuthenticationError(
                    f"Authentication failed for {resource_type}: {error_message}",
                    status_code=status_code,
                    response=response,
                )
            elif status_code == 403:
                raise JiraPermissionError(
                    f"Permission denied for {resource_type} {resource_id}: {error_message}",
                    status_code=status_code,
                    response=response,
                )
            elif status_code == 404:
                raise JiraResourceNotFoundError(
                    f"{resource_type.capitalize()} {resource_id} not found: {error_message}",
                    status_code=status_code,
                    response=response,
                )

        # Default error handling
        if "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            raise JiraAuthenticationError(
                f"Authentication failed for {resource_type}: {error_message}",
                status_code=status_code,
                response=response,
            )
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            raise JiraPermissionError(
                f"Permission denied for {resource_type} {resource_id}: {error_message}",
                status_code=status_code,
                response=response,
            )
        elif "not found" in error_message.lower() or "does not exist" in error_message.lower():
            raise JiraResourceNotFoundError(
                f"{resource_type.capitalize()} {resource_id} not found: {error_message}",
                status_code=status_code,
                response=response,
            )
        else:
            raise JiraAPIError(
                f"Error accessing {resource_type} {resource_id}: {error_message}",
                status_code=status_code,
                response=response,
            )

    def get_jira_field_ids(self) -> Dict[str, str]:
        """
        Discover Jira field IDs dynamically.

        This method queries the Jira API to find the correct custom field IDs
        for various fields, which can vary between different Jira instances.

        Returns:
            Dictionary mapping field names to their IDs.
        """
        try:
            # Check if we've already cached the field IDs
            if self._field_ids_cache:
                return self._field_ids_cache

            # Fetch all fields from Jira API
            fields = self.jira.fields()
            field_ids = {}

            # Log the complete list of fields for debugging
            all_field_names = [f"{field.get('name', '')} ({field.get('id', '')})" for field in fields]
            logger.debug(f"All available Jira fields: {all_field_names}")

            # Look for fields - use multiple strategies to identify them
            for field in fields:
                field_name = field.get("name", "").lower()
                original_name = field.get("name", "")
                field_id = field.get("id", "")
                field_schema = field.get("schema", {})
                field_type = field_schema.get("type", "")
                field_custom = field_schema.get("custom", "")

                # Epic Link field - used to link issues to epics
                if (
                    "epic link" in field_name
                    or "epic-link" in field_name
                    or original_name == "Epic Link"
                    or field_custom == "com.pyxis.greenhopper.jira:gh-epic-link"
                ):
                    field_ids["epic_link"] = field_id
                    logger.info(f"Found Epic Link field: {original_name} ({field_id})")

                # Epic Name field - used when creating epics
                elif (
                    "epic name" in field_name
                    or "epic-name" in field_name
                    or original_name == "Epic Name"
                    or field_custom == "com.pyxis.greenhopper.jira:gh-epic-label"
                ):
                    field_ids["epic_name"] = field_id
                    logger.info(f"Found Epic Name field: {original_name} ({field_id})")

                # Parent field - sometimes used instead of Epic Link
                elif field_name == "parent" or field_name == "parent link" or original_name == "Parent Link":
                    field_ids["parent"] = field_id
                    logger.info(f"Found Parent field: {original_name} ({field_id})")

                # Epic Status field
                elif "epic status" in field_name or original_name == "Epic Status":
                    field_ids["epic_status"] = field_id
                    logger.info(f"Found Epic Status field: {original_name} ({field_id})")

                # Epic Color field
                elif (
                    "epic colour" in field_name
                    or "epic color" in field_name
                    or original_name == "Epic Colour"
                    or original_name == "Epic Color"
                    or field_custom == "com.pyxis.greenhopper.jira:gh-epic-color"
                ):
                    field_ids["epic_color"] = field_id
                    logger.info(f"Found Epic Color field: {original_name} ({field_id})")

                # Priority field
                elif field_name == "priority" or original_name == "Priority":
                    field_ids["priority"] = field_id
                    logger.info(f"Found Priority field: {original_name} ({field_id})")

                # Sprint field
                elif "sprint" in field_name or field_custom == "com.pyxis.greenhopper.jira:gh-sprint":
                    field_ids["sprint"] = field_id
                    logger.info(f"Found Sprint field: {original_name} ({field_id})")

                # Story Points field
                elif "story points" in field_name or "storypoints" in field_name or "story point" in field_name:
                    field_ids["story_points"] = field_id
                    logger.info(f"Found Story Points field: {original_name} ({field_id})")

                # Try to detect any other fields that might be related to core functionality
                elif ("epic" in field_name or "epic" in field_custom) and field_id not in field_ids.values():
                    key = f"epic_{field_name.replace(' ', '_')}"
                    field_ids[key] = field_id
                    logger.info(f"Found additional Epic-related field: {original_name} ({field_id})")

            # Cache the results for future use
            self._field_ids_cache = field_ids
            return field_ids

        except Exception as e:
            logger.error(f"Error discovering Jira field IDs: {str(e)}")
            self._handle_error(e, "fields")
            # Return an empty dict as fallback
            return {}

    def get_current_user_account_id(self) -> str:
        """
        Get the account ID of the current user.

        Returns:
            The account ID string of the current user

        Raises:
            JiraAuthenticationError: If unable to get the current user's account ID
        """
        try:
            myself = self.jira.myself()
            account_id: Optional[str] = myself.get("accountId")
            if not account_id:
                raise JiraAuthenticationError("Unable to get account ID from user profile")
            return account_id
        except Exception as e:
            logger.error(f"Error getting current user account ID: {str(e)}")
            self._handle_error(e, "user", "current")
