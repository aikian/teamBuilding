"""
Association table for users in teams.

Links a user to a team and tracks the user's role (leader or member)
and when they joined. This is similar to ``ClassMember`` but for
teams.
"""

from database import db
from .base import BaseModel


class TeamMember(BaseModel):
    __tablename__ = "team_members"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="MEMBER")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("team_id", "user_id", name="uq_team_member"),) #같은 팀에 같은 유저가 중복으로 가입되지 않도록 제한 추가