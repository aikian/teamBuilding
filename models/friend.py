"""
친구 관계 모델 정의입니다.

두 사용자 간의 단방향 친구 관계를 나타내며,
status 필드는 관계 상태(pending, accepted, blocked, deleted)를 추적합니다.
"""


from database import db
from .base import BaseModel


class Friend(BaseModel):
    __tablename__ = "friends"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("user_id", "friend_id", name="uq_friend_pair"),) #동일한 user_id, friend_id 쌍의 친구 관계가 중복으로 생기지 않도록 제약 추가

    def __repr__(self) -> str:
        return f"<Friend {self.user_id}->{self.friend_id} ({self.status})>"