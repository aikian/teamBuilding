"""
프로필 모델 정의입니다.

사용자의 성격, 목표, 기술 스킬 등 확장된 프로필 정보를 저장합니다.
이 데이터는 매칭 알고리즘에서 적합한 팀을 찾는 데 사용됩니다.
"""


from database import db
from .base import BaseModel


class Profile(BaseModel):
    __tablename__ = "profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    personality = db.Column(db.String(255))
    goals = db.Column(db.String(255))
    skills = db.Column(db.String(255))

    __table_args__ = (db.UniqueConstraint("user_id", name="uq_profile_user"),) #한 유저가 하나의 프로필만 가지도록 제약 추가