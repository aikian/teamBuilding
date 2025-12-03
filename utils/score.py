"""
Score calculation utilities.

Defines helper functions to compute match scores between users and
teams. For simplicity these functions wrap the logic from
``MatchingService``.
"""

from models.user import User
from models.team import Team
from services.matching_service import MatchingService


def calculate_match_score(user: User, team: Team) -> int:
    """Compute the matching score for a user and a team."""
    return MatchingService.calculate_score(user, team)