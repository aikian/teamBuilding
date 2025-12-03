"""
Service layer for notifications.

Creates and manages notifications for users. This simplified service
writes notifications to the database; it could be extended to send
email or push notifications.
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