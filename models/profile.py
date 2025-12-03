"""
Profile model definition.

Stores extended profile information for a user, such as personality
traits, goals and technical skills. This data is used by the matching
algorithm to find suitable teams.
"""

from database import db
from .base import BaseModel


class Profile(BaseModel):
    __tablename__ = "profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    personality = db.Column(db.String(255))
    goals = db.Column(db.String(255))
    skills = db.Column(db.String(255))

    __table_args__ = (db.UniqueConstraint("user_id", name="uq_profile_user"),) #한 유저가 하나의 프로필만 가지도록 제약 추가