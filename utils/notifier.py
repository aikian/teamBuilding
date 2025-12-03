"""
Notifier helper functions.

Provides convenience wrappers around ``NotificationService`` to send
common types of notifications. This keeps the services focused on
core business logic while encapsulating notification details here.
"""

from typing import Optional

from services.notification_service import NotificationService


def notify_invitation(to_user_id: int, team_id: int) -> None:
    """Send a team invitation notification."""
    message = "팀 초대가 도착했습니다."
    NotificationService.send_notification(to_user_id, type="INVITATION", message=message, related_id=team_id)


def notify_application_result(user_id: int, team_id: int, accepted: bool) -> None:
    """Notify a user about the result of a team application."""
    if accepted:
        message = "팀 지원이 승인되었습니다."
        type_ = "APPROVED"
    else:
        message = "팀 지원이 거절되었습니다."
        type_ = "REJECTED"
    NotificationService.send_notification(user_id, type=type_, message=message, related_id=team_id)