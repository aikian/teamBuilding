"""
매칭 요청 모델입니다.

팀장이 특정 기준에 따라 잠재적인 팀원을 찾기 위해 요청한 내용을 저장합니다.
"""

from database import db
from .base import BaseModel


class MatchingRequest(BaseModel):
    __tablename__ = "matching_requests"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False) #요청 시점은 항상 존재해야하기에 'nullable=False' 추가