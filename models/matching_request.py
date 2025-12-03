"""
Matching request model.

Stores a team leader's request to find potential members according to
certain criteria. It could be extended to include weights for
personality, skills and goals. For simplicity we just store the team
and a timestamp.
"""

from database import db
from .base import BaseModel


class MatchingRequest(BaseModel):
    __tablename__ = "matching_requests"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False) #요청 시점은 항상 존재해야하기에 'nullable=False' 추가