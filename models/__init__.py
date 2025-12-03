"""Model package initialiser."""
# Import all models so SQLAlchemy can discover them for table creation
from .user import User
from .profile import Profile
from .friend import Friend
from .class_ import ClassRoom
from .class_member import ClassMember
from .category import Category
from .team import Team
from .team_member import TeamMember
from .team_application import TeamApplication
from .team_invitation import TeamInvitation
from .notification import Notification
from .matching_request import MatchingRequest

__all__ = [
    "User",
    "Profile",
    "Friend",
    "ClassRoom",
    "ClassMember",
    "Category",
    "Team",
    "TeamMember",
    "TeamApplication",
    "TeamInvitation",
    "Notification",
    "MatchingRequest",
]
