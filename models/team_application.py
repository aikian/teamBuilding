"""
팀 가입 신청 모델입니다.

사용자가 팀에 가입하기 위해 제출한 신청을 저장하며,
팀장은 해당 신청을 승인하거나 거절할 수 있습니다.
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