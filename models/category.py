"""
카테고리 모델 정의입니다.

팀을 포함할 수 있는 카테고리나 관심 분야를 나타냅니다.
사용자는 관심사로 카테고리를 선택할 수 있으며,
팀은 특정 카테고리에 속할 수 있습니다.
"""


from database import db
from .base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    teams = db.relationship("Team", backref="category")