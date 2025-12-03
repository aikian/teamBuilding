"""
알림 기능 블루프린트

- 현재 로그인한 사용자에게 초대, 승인, 거절 등 알림 목록 표시
- NotificationService를 통해 알림 읽음 처리
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash

from models.notification import Notification
from services.notification_service import NotificationService

notification_bp = Blueprint("notification", __name__)

# ----------------------------
# / (list_notifications)
# 사용자 알림 목록 조회
# ----------------------------
@notification_bp.route("/")
def list_notifications():
    """
    현재 로그인한 사용자의 알림 목록 표시

    - 로그인 안 되어 있으면 로그인 페이지로 리다이렉트
    - 알림은 생성일 기준 내림차순으로 정렬
    - TEST: 로그인/로그아웃 상태, 알림 정렬 확인
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))

    notifications = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("notification_list.html", notifications=notifications)


# ----------------------------
# /<notification_id>/read
# 알림 읽음 처리
# ----------------------------
@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id: int):
    """
    특정 알림을 읽음 처리

    - 로그인하지 않으면 로그인 페이지로 리다이렉트
    - NotificationService를 통해 read 상태 업데이트
    - 요청 후 이전 페이지(referrer) 또는 알림 목록으로 리다이렉트
    - TEST: read 상태 반영 여부 확인
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    NotificationService.mark_as_read(notification_id, user_id)
    return redirect(request.referrer or url_for("notification.list_notifications"))
