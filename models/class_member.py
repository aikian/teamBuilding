"""
Association table for users in classes.

This model links a user to a class and stores the user's role
within the class (e.g., member or admin). It allows many-to-many
relationships between users and classes.
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