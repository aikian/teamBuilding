"""
사용자 관련 기능을 제공하는 서비스 레이어입니다.

사용자 생성 및 검증과 관련된 비즈니스 로직을 포함하며,
보안을 위해 비밀번호는 해시 처리됩니다. 추가 프로필 정보는
``Profile`` 모델에 저장됩니다.
"""

from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from models.user import User
from models.profile import Profile
from models.team_member import TeamMember
from models.class_member import ClassMember
from models.friend import Friend


class UserService:
    """Encapsulates user-related business logic."""

    @staticmethod
    # 사용자 생성
    def create_user(
        username: str,
        password: str,
        name: str,
        student_no: str,
        school: Optional[str],
        personality: Optional[str],
        goals: Optional[str],
        skills: Optional[str],
    ) -> User:
        """Create a new user and associated profile.

        Raises:
            ValueError: if the username or student_no is already taken.
        """
        # 1. 중복 가입 방지
        if User.query.filter((User.username == username) | (User.student_no == student_no)).first():
            raise ValueError("이미 존재하는 사용자입니다.")

        # 2. 비밀번호
        hashed_pw = generate_password_hash(password)
        user = User(
            username=username,
            password=hashed_pw,
            name=name,
            student_no=student_no,
            school=school,
        )

        # 3. 유저 아이디 생성
        db.session.add(user)
        db.session.flush() 

        # 4. 프로필 정보 생성 및 연결
        profile = Profile(
            user_id=user.id,
            personality=personality,
            goals=goals,
            skills=skills,
        )
        db.session.add(profile)
        # 최종저장
        db.session.commit()
        return user

    @staticmethod
    # 사용자 인증(로그인)
    def verify_user(username: str, password: str) -> Optional[User]:
        """Verify user credentials and return the user object if valid."""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        if not check_password_hash(user.password, password):
            return None
        return user

    @staticmethod
    # 프로필 업데이트
    def update_profile(
        user_id: int,
        name: Optional[str],
        school: Optional[str],
        personality: Optional[str],
        goals: Optional[str],
        skills: Optional[str],
    ) -> User:
        """Update the basic and profile information of a user."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        if name:
            user.name = name
        user.school = school
        profile = user.profile
        if not profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
        profile.personality = personality
        profile.goals = goals
        profile.skills = skills
        db.session.commit()
        return user

    @staticmethod
    # 사용자 탈퇴
    def delete_user(user_id: int) -> None:
        """Delete a user after ensuring they are not blocking leader of any team."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")
        # 1. 탈퇴 방지 조건 체크
        blocking_messages = []
        leader_memberships = TeamMember.query.filter_by(user_id=user_id, role="LEADER").all()
        for membership in leader_memberships:
            others = TeamMember.query.filter(
                TeamMember.team_id == membership.team_id,
                TeamMember.user_id != user_id,
            ).count()
            team_name = membership.team.name if membership.team else f"팀 {membership.team_id}"
            if others > 0:
                blocking_messages.append(f"{team_name} 팀장 권한을 다른 팀원에게 위임해주세요.")
            else:
                blocking_messages.append(f"{team_name} 팀을 해체한 후 탈퇴가 가능합니다.")
        if blocking_messages:
            raise ValueError("탈퇴 전 조치 필요: " + " / ".join(blocking_messages))
        # 2. 데이터 정리
        from services.team_service import TeamService

        memberships = TeamMember.query.filter_by(user_id=user_id).all()
        for membership in memberships:
            TeamService.remove_member(membership.team_id, user_id, user_id)

        ClassMember.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Friend.query.filter(
            (Friend.user_id == user_id) | (Friend.friend_id == user_id)
        ).delete(synchronize_session=False)
        # 3. 사용자 및 프로필 삭제
        if user.profile:
            db.session.delete(user.profile)
        db.session.delete(user)
        db.session.commit()