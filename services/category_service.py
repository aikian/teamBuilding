"""
Service layer for category operations.

Allows creation of categories and retrieval of all categories. Teams
may be associated with a category.
"""

from typing import List

from database import db
from models.category import Category


class CategoryService:
    """Business logic for categories."""

    @staticmethod
    def create_category(name: str, created_by: int = None) -> Category:
        """Create a new category."""
        # 1. 중복된 이름이 있는지 확인
        if Category.query.filter_by(name=name).first():
            raise ValueError("이미 존재하는 카테고리입니다.")
        
        # 2. 카테고리 객체 생성 및 DB 저장
        category = Category(name=name, created_by=created_by)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def list_categories() -> List[Category]:
        """Return all available categories."""
        return Category.query.all()