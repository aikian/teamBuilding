"""
알림 관련 기능을 제공하는 서비스 레이어입니다.

사용자 알림을 생성하고 관리합니다. 이 단순 구현에서는
알림을 데이터베이스에 기록하지만, 필요시 푸시 알림
전송 기능으로 확장할 수 있습니다.
"""

from typing import Optional

from database import db
from models.notification import Notification


class NotificationService:
    """Responsible for persisting notifications."""

    @staticmethod
    # 알림 보내기
    def send_notification(user_id: int, type: str, message: str, related_id: Optional[int] = None) -> Notification:
        """Create and save a notification."""
        notification = Notification(
            user_id=user_id,
            type=type,
            message=message,
            related_id=related_id,
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    # 읽음 처리
    def mark_as_read(notification_id: int, user_id: int) -> None:
        """Mark a notification as read if it belongs to the user."""
        notification = Notification.query.get(notification_id)
        # 1. 유효성 및 권한 검사
        if not notification or notification.user_id != user_id:
            return
        # 2. 중복 처리 방지
        if notification.read_at:
            return
        # 3. 읽은 시간을 서버 시간으로 업데이트
        notification.read_at = db.func.now()
        db.session.commit()