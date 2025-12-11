"""
클래스 내 사용자 연결 테이블입니다.

이 모델은 사용자를 클래스와 연결하고, 클래스 내에서
사용자의 역할(예: 멤버, 관리자)을 저장합니다.
이를 통해 사용자와 클래스 간 다대다 관계를 표현할 수 있습니다.
"""


from database import db
from .base import BaseModel


class ClassMember(BaseModel):
    __tablename__ = "class_members"

    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="MEMBER")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("class_id", "user_id", name = "uq_class_user"),) #동일 유저가 같은 클래스에 중복 가입하지 않도록 하기 위해 제약 추가