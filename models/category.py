"""
Category model definition.

Represents a category or interest area that can host teams. Users may
select categories as their interests, and teams may be associated
with a category.
"""

from database import db
from .base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    teams = db.relationship("Team", backref="category")