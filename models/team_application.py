"""
Team application model.

Stores a user's application to join a team. The application can be
approved or rejected by the team leader.
"""

from database import db
from .base import BaseModel


class TeamApplication(BaseModel):
    __tablename__ = "team_applications"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    decided_at = db.Column(db.DateTime, nullable=True)