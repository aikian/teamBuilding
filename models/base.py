"""
SQLAlchemy 모델을 위한 기본 믹스인 클래스입니다.

이 클래스를 상속하는 모든 테이블에 정수형 기본 키 ``id`` 컬럼을 제공합니다.
클래스를 추상 클래스로 표시했기 때문에 ``BaseModel`` 자체에 대한 테이블은 생성되지 않습니다.
"""


from database import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)