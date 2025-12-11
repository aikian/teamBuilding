"""
ClassRoom 모델 정의입니다.

학교 수업이나 조직과 같은 클래스는 여러 팀을 포함할 수 있습니다.
``code`` 필드는 사용자가 참여할 수 있는 고유한 참여 코드를 저장합니다.
"""


from database import db
from .base import BaseModel


class ClassRoom(BaseModel):
    __tablename__ = "classes"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="ACTIVE")
    delete_at = db.Column(db.DateTime, nullable=True)

    # Backref definitions allow easy access to related objects.
    members = db.relationship("ClassMember", backref="class_room", cascade="all, delete-orphan")
    teams = db.relationship("Team", backref="class_room")