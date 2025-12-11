"""
팀 초대 모델입니다.

팀장이 사용자에게 보낸 초대를 나타내며,
초대 상태는 pending, accepted, rejected가 될 수 있습니다.
수락 시 사용자가 팀에 추가됩니다.
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