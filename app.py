"""
팀 빌딩 웹 애플리케이션의 메인 진입점입니다.
Flask 앱 생성, 설정 적용, DB 초기화 및 블루프린트 등록을 수행합니다.
"""

from flask import Flask, render_template

from config import Config
from database import db
from datetime import timedelta  # KST 변환용

# SQLAlchemy가 모델을 인식하도록 모델 전체 import
import models  # noqa: F401

# 도메인별 블루프린트
from controllers.user_controller import user_bp
from controllers.friend_controller import friend_bp
from controllers.class_controller import class_bp
from controllers.team_controller import team_bp
from controllers.category_controller import category_bp
from controllers.matching_controller import matching_bp
from controllers.notification_controller import notification_bp


def create_app() -> Flask:
    """Flask 앱 생성 및 설정을 적용하는 팩토리 함수."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # DB 초기화
    db.init_app(app)

    # 블루프린트 등록
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(friend_bp, url_prefix="/friends")
    app.register_blueprint(class_bp, url_prefix="/classes")
    app.register_blueprint(team_bp, url_prefix="/teams")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(matching_bp, url_prefix="/matching")
    app.register_blueprint(notification_bp, url_prefix="/notifications")

    # UTC 시간을 KST(+9)로 변환하는 템플릿 필터
    @app.template_filter("kst")
    def to_kst(value):
        if not value:
            return ""
        return (value + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")

    # 홈 페이지
    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    # 최초 실행 시 테이블 생성 후 개발 서버 실행
    with application.app_context():
        db.create_all()
    application.run(debug=True)
