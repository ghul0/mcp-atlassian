"""
Exceptions for the Jira API module.
"""


class JiraAPIError(Exception):
    """Base exception for Jira API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class JiraAuthenticationError(JiraAPIError):
    """Exception for authentication errors."""

    pass


class JiraPermissionError(JiraAPIError):
    """Exception for permission errors."""

    pass


class JiraResourceNotFoundError(JiraAPIError):
    """Exception for resource not found errors."""

    pass


class JiraFieldError(JiraAPIError):
    """Exception for field validation errors."""

    pass


class JiraIssueTypeError(JiraAPIError):
    """Exception for issue type errors."""

    pass


class JiraWorkflowError(JiraAPIError):
    """Exception for workflow transition errors."""

    pass


class JiraConfigurationError(Exception):
    """Exception for configuration errors."""

    pass
