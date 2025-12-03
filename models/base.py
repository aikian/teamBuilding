"""
Base model mixin for SQLAlchemy models.

Provides an integer primary key ``id`` column on all tables that
inherit from it. By marking the class as abstract SQLAlchemy will
not create a table for ``BaseModel`` itself.
"""

from database import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)