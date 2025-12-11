"""
알림 모델 정의입니다.

사용자에게 전송되는 알림을 나타냅니다. 초대, 승인, 거절, 추방 등
여러 상황에 활용될 수 있으며, type 필드는 알림 종류를,
related_id는 관련 초대, 신청, 팀 등의 ID를 저장할 수 있습니다.
"""


from database import db
from .base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    related_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    read_at = db.Column(db.DateTime, nullable=True)