"""
애플리케이션 설정입니다.

이 모듈은 Flask 애플리케이션에서 사용할 기본 설정들을 담은
간단한 설정 클래스를 정의합니다. 개발 환경에서는 로컬 SQLite
데이터베이스를 사용하며, 배포 환경에서는 환경 변수를 통해
데이터베이스 URI나 기타 설정들을 변경할 수 있습니다.
"""

import os


class Config:
    """Flask 애플리케이션 설정 클래스입니다."""

    # Flask 세션 쿠키 보호를 위한 시크릿 키입니다.
    # 배포 환경에서는 충분히 강력한 랜덤 값으로 반드시 교체해야 합니다.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # 현재 파일의 기준 경로를 가져와 경로 설정에 사용합니다.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # SQLAlchemy에서 사용할 데이터베이스 URI입니다.
    # 개발 단계에서는 SQLite를 기본으로 사용하며,
    # 필요하다면 PostgreSQL 또는 MySQL URI로 변경할 수 있습니다.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )

    # 모델 변경이 발생할 때마다 애플리케이션에 신호를 보내는 기능을 비활성화합니다.
    # 불필요한 오버헤드가 발생할 수 있기 때문에 대부분의 경우 끄는 것이 좋습니다.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
