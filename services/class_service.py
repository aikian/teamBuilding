"""
Service layer for class operations.

Responsible for creating classes, joining classes via code, and
listing classes for a user. It encapsulates business rules such as
unique join codes and membership management.
"""

import random
import string
from typing import List

from database import db
from models.class_ import ClassRoom
from models.class_member import ClassMember


class ClassService:
    """Class-related business logic."""

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        """Generate a random join code composed of uppercase letters and digits."""
        chars = string.ascii_uppercase + string.digits
        while True:
            #생성된 코드가 DB에 존재하는지 중복확인
            code = "".join(random.choice(chars) for _ in range(length))
            if not ClassRoom.query.filter_by(code=code).first():
                return code

    @staticmethod
    def create_class(owner_id: int, name: str, description: str) -> ClassRoom:
        """Create a new class and assign the owner as its admin."""
        code = ClassService._generate_code()
        clazz = ClassRoom(name=name, description=description, code=code, owner_id=owner_id)
        db.session.add(clazz)
        db.session.flush()
        # 생성자를 관리자 권한으로 멤버에 추가
        member = ClassMember(class_id=clazz.id, user_id=owner_id, role="ADMIN")
        db.session.add(member)
        db.session.commit()
        return clazz

    @staticmethod
    def join_class(user_id: int, code: str) -> ClassMember:
        """Join an existing class by its code."""
        # 1. 코드로 클래스 조회
        clazz = ClassRoom.query.filter_by(code=code).first()
        if not clazz:
            raise ValueError("코드에 해당하는 클래스가 존재하지 않습니다.")
        # 2. 이미 가입된 사용자인지 확인
        if ClassMember.query.filter_by(class_id=clazz.id, user_id=user_id).first():
            raise ValueError("이미 참여 중인 클래스입니다.")
        # 3. 일반 멤버 권한으로 가입 처리
        member = ClassMember(class_id=clazz.id, user_id=user_id, role="MEMBER")
        db.session.add(member)
        db.session.commit()
        return member

    @staticmethod
    def get_classes_for_user(user_id: int) -> List[ClassRoom]:
        """Return all classes that a user is a member of."""
        if not user_id:
            return []
        #사용자의 모든 멤버십 정보 조회
        memberships = ClassMember.query.filter_by(user_id=user_id).all()
        #멤버십에서 클래스 ID만 조회
        class_ids = [m.class_id for m in memberships]
        #ID리스트에 포함된 클래스들을 한 번에 조회
        return ClassRoom.query.filter(ClassRoom.id.in_(class_ids)).all() if class_ids else []