"""
Authentication utilities.

This module contains helper functions for hashing and verifying
passwords. Although ``werkzeug.security`` is used directly in
``UserService``, centralising these helpers here makes it easy to
swap in a different hashing algorithm later if needed.
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Return a hashed password string."""
    return generate_password_hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    """Verify a password against its hashed value."""
    return check_password_hash(hashed_password, password)