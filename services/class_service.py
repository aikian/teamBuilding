"""
클래스 관련 기능을 제공하는 서비스 레이어입니다.

클래스 생성, 코드로 클래스 참여, 사용자의 클래스 목록 조회를 담당하며,
고유 참여 코드와 멤버십 관리 같은 비즈니스 규칙을 포함합니다.
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
    
    @staticmethod
    def dissolve_class(class_id: int, by_user_id: int) -> None:
        """클래스를 해체하고, 클래스 내 팀과 사용자에게 알림을 전송합니다."""
        from services.notification_service import NotificationService
        from models.team import Team
        from models.team_member import TeamMember

        # 1. 클래스 존재 여부 확인
        clazz = ClassRoom.query.get(class_id)
        if not clazz:
            raise ValueError("존재하지 않는 클래스입니다.")

        # 2. 클래스 관리자 권한 확인
        if clazz.owner_id != by_user_id:
            raise ValueError("클래스를 해체할 권한이 없습니다.")

        # 3. 클래스 내 모든 팀 해체
        teams = Team.query.filter_by(class_id=class_id).all()
        for team in teams:
            # 팀 멤버에게 알림 전송
            members = TeamMember.query.filter_by(team_id=team.id).all()
            for mem in members:
                if mem.user_id != by_user_id:
                    NotificationService.send_notification(
                        mem.user_id,
                        "TEAM_DISSOLVED",
                        f"[{team.name}] 팀이 클래스 해체로 인해 삭제되었습니다.",
                        related_id=team.id
                    )
            # 팀 삭제
            db.session.delete(team)

        # 4. 클래스 멤버에게 알림 전송 후 삭제
        class_members = ClassMember.query.filter_by(class_id=class_id).all()
        for mem in class_members:
            if mem.user_id != by_user_id:
                NotificationService.send_notification(
                    mem.user_id,
                    "CLASS_DISSOLVED",
                    f"[{clazz.name}] 클래스가 해체되었습니다.",
                    related_id=class_id
                )
            db.session.delete(mem)

        # 5. 클래스 자체 삭제
        db.session.delete(clazz)
        db.session.commit()