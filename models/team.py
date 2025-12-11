"""
팀 모델 정의입니다.

클래스 또는 카테고리 내 팀을 나타내며, 각 팀은 이름, 목표,
필요 기술, 정원을 가집니다. 팀은 클래스나 카테고리 중
하나에만 속할 수 있습니다.
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