"""
인증 관련 기능을 제공하는 서비스입니다.
컨트롤러에서 인증 로직을 분리하고, 필요시 JWT 생성도 처리할 수 있습니다.

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