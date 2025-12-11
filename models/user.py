"""
사용자 모델 정의입니다.

시스템에 등록된 사용자를 나타내며, 각 사용자는 고유한
username과 학번, 해시된 비밀번호, 이름을 가집니다.
사용자는 연결 테이블을 통해 여러 클래스와 팀에 속할 수 있습니다.
"""


from database import db
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    student_no = db.Column(db.String(20), unique=True, nullable=False)
    school = db.Column(db.String(100))

    # One-to-one relationship to Profile. ``uselist=False`` makes
    # SQLAlchemy return a single object rather than a list.
    profile = db.relationship("Profile", backref="user", uselist=False)

    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)  # 클래스 테이블에 외래키로 연결
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    