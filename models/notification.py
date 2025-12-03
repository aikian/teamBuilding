"""
Notification model definition.

Represents a notification sent to a user. Notifications can be used
for invites, acceptances, rejections, expulsions, etc. The type
field indicates the kind of notification, and related_id can store
the associated invitation, application, or team id.
"""

from database import db
from .base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    related_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    read_at = db.Column(db.DateTime, nullable=True)