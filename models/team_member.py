"""
팀 내 사용자 연결 테이블입니다.

사용자를 팀과 연결하고 사용자의 역할(리더 또는 멤버)과
참여 시점을 기록합니다. ``ClassMember``와 유사하지만 팀용입니다.
"""


from database import db
from .base import BaseModel


class TeamMember(BaseModel):
    __tablename__ = "team_members"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="MEMBER")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("team_id", "user_id", name="uq_team_member"),) #같은 팀에 같은 유저가 중복으로 가입되지 않도록 제한 추가