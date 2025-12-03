"""
Input validation utilities.

This module defines simple validation functions to ensure inputs meet
certain criteria. These helpers can be used throughout the service
layer to enforce basic constraints.
"""


def validate_non_empty(value: str, field_name: str) -> None:
    """Raise an error if the given value is empty."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} 값이 필요합니다.")