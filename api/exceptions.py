class HTTPStatus(Exception):
    """Exception raised for an unexpected HTTP status code from the server.

    Attributes:
        status_code: The HTTP status code that was returned by the server.
    """

    def __init__(self, status_code):
        """Initialize the HTTPStatus exception.

        Args:
            status_code: The HTTP status code that was returned by the server.
        """
        self.status_code = status_code

    def __str__(self):
        """Return a string representation of the HTTPStatus exception."""
        return f"Unexpected status code from server: {self.status_code}"


class SessionExpiredError(Exception):
    """Exception raised when the session has expired and cannot be refreshed.

    This exception is raised when the API session has expired and the
    automatic refresh mechanism was unable to restore the session.
    """

    def __init__(self, message="Session has expired and could not be refreshed"):
        """Initialize the SessionExpiredError exception.

        Args:
            message: A custom error message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Return a string representation of the SessionExpiredError exception."""
        return self.message
