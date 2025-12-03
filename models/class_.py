"""
ClassRoom model definition.

A class (such as a school class or organisation) can contain many
teams. The ``code`` field stores a unique join code for users to join
without scanning a QR code.
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
    deleted_at = db.Column(db.DateTime, nullable=True)  #deleted가 더 정확하기에 'delete'에서 'deleted'로 수정

    # Backref definitions allow easy access to related objects.
    members = db.relationship("ClassMember", backref="class_room", cascade="all, delete-orphan")
    teams = db.relationship("Team", backref="class_room")