"""
팀 빌딩 애플리케이션의 데이터베이스입니다.

이 모듈은 SQLAlchemy 인스턴스를 감싸 두어 애플리케이션이 생성될 때
초기화할 수 있도록 합니다. 모델에서 ``db``를 import해 사용하면
SQLAlchemy가 모든 테이블 정의를 자동으로 추적할 수 있습니다.
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 객체 생성.
# 실제 초기화는 ``app.py``의 ``create_app`` 함수에서 Flask 앱과 함께 이루어집니다.
db = SQLAlchemy()
