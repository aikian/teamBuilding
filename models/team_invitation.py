"""
Team invitation model.

Represents an invitation sent by a team leader to a user. The
invitation can be pending, accepted or rejected. On acceptance the
user is added to the team.
"""

from database import db
from .base import BaseModel


class TeamInvitation(BaseModel):
    __tablename__ = "team_invitations"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    responded_at = db.Column(db.DateTime, nullable=True)