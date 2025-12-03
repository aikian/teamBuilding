"""
User model definition.

Represents a registered user in the system. Each user has a unique
username and student number, a hashed password and a name. A user may
belong to many classes and teams through association tables.
"""

from database import db
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    student_no = db.Column(db.String(20), unique=True, nullable=False)
    school = db.Column(db.String(100))

    # One-to-one relationship to Profile. ``uselist=False`` makes
    # SQLAlchemy return a single object rather than a list.
    profile = db.relationship("Profile", backref="user", uselist=False)