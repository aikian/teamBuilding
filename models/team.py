"""
Team model definition.

Represents a team within a class or category. Each team has a name,
goal, required skills and capacity. It may belong to either a class
or a category (but not both).
"""

from database import db
from .base import BaseModel


class Team(BaseModel):
    __tablename__ = "teams"

    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text)
    required_skills = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    recruit_status = db.Column(db.String(20), default="OPEN")
    # Optional open chat URL for team meetings or external chat invitations
    openchat_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    members = db.relationship("TeamMember", backref="team", cascade="all, delete-orphan")