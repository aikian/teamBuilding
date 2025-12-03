"""
Service for authentication-related helpers.

For a simple application we don't need much here, but this class is
defined to illustrate how authentication might be abstracted away
from controllers. In a larger system you might generate JWTs here.
"""

from flask import session


class AuthService:
    """Utility methods for managing authentication."""

    @staticmethod
    def login_user(user_id: int) -> None:
        """Store the user's ID in the session."""
        session["user_id"] = user_id

    @staticmethod
    def logout_user() -> None:
        """Clear the session."""
        session.clear()

    @staticmethod
    def current_user_id() -> int:
        """Return the ID of the currently logged-in user, if any."""
        return session.get("user_id")