"""
Service layer for friend operations.

Handles searching for users, sending friend requests, accepting or
blocking, and listing friends. In this minimal implementation we
store friend relationships as a single row with a status indicating
whether the friendship is pending, accepted, or blocked.
"""

from typing import List

from database import db
from models.user import User
from models.friend import Friend


class FriendService:
    """Encapsulates friendship-related business logic."""

    @staticmethod
    # 유저 검색
    def search_users(keyword: str) -> List[User]:
        """Search users by partial match on name or student number."""
        #대소문자 구분 없이 일치 검색
        return User.query.filter(
            (User.name.ilike(f"%{keyword}%")) | (User.student_no.ilike(f"%{keyword}%"))
        ).all()

    @staticmethod
    # 친구요청
    def send_request(user_id: int, target_id: int) -> None:
        """Send a friend request from user_id to target_id."""
        if user_id == target_id:
            raise ValueError("자기 자신에게는 친구 요청을 보낼 수 없습니다.")
        # 이미 친구이거나, 요청 대기 중이거나, 차단된 관계인지 확인
        existing = Friend.query.filter_by(user_id=user_id, friend_id=target_id).first()
        if existing:
            raise ValueError("이미 친구이거나 요청 중인 사용자입니다.")
        # 상태를 PENDING으로 설정하여 요청 생성
        request = Friend(user_id=user_id, friend_id=target_id, status="PENDING")
        db.session.add(request)
        db.session.commit()

    @staticmethod
    # 아이디 조회 후 친구요청
    def send_request_by_username(user_id: int, username: str) -> None:
        """Lookup a target user by username and send a request."""
        target = User.query.filter_by(username=username).first()
        if not target:
            raise ValueError("해당 아이디를 가진 사용자를 찾을 수 없습니다.")
        #ID를 찾은 후 실제 요청 로직 위임
        FriendService.send_request(user_id, target.id)

    @staticmethod
    # 요청 수락
    def accept_request(request_id: int, current_user_id: int) -> None:
        """Accept a friend request."""
        req = Friend.query.get(request_id)
        # 요청이 존재하며, 받는 사람이 현재 사용자이고, 상태가 대기 중인지 검증
        if req and req.friend_id == current_user_id and req.status == "PENDING":
            req.status = "ACCEPTED"
            # 상호관계 생성
            reciprocal = Friend(user_id=req.friend_id, friend_id=req.user_id, status="ACCEPTED")
            db.session.add(reciprocal)
            db.session.commit()

    @staticmethod
    # 차단
    def block_user(user_id: int, target_id: int) -> None:
        """Block a user from sending future friend requests."""
        relation = Friend.query.filter_by(user_id=user_id, friend_id=target_id).first()
        if not relation:
            #기존 관계가 없다면 새로 생성
            relation = Friend(user_id=user_id, friend_id=target_id)
            db.session.add(relation)

        # 상태를 BLOCKED로 설정
        relation.status = "BLOCKED"
        db.session.commit()

    @staticmethod
    # 친구 목록
    def list_friends(user_id: int) -> List[User]:
        """Return a list of User objects that are friends with the given user."""
        relations = Friend.query.filter_by(user_id=user_id, status="ACCEPTED").all()
        friend_ids = [rel.friend_id for rel in relations]
        #친구들의 ID 리스트로 User 테이블에서 실제 정보 조회
        return User.query.filter(User.id.in_(friend_ids)).all() if friend_ids else []

    @staticmethod
    # 요청 대기 중인 친구 목록
    def list_pending_requests(user_id: int) -> List[Friend]:
        """Return a list of pending Friend requests where the current user is the target."""
        #friend_id가 본인인 경우를 조회
        return Friend.query.filter_by(friend_id=user_id, status="PENDING").all()

    @staticmethod
    # 친구삭제
    def remove_friend(user_id: int, target_id: int) -> None:
        """Remove an accepted friend relationship between two users."""
        # 양방향 모두 조회하여 삭제
        rel1 = Friend.query.filter_by(user_id=user_id, friend_id=target_id).first()
        rel2 = Friend.query.filter_by(user_id=target_id, friend_id=user_id).first()
        for rel in (rel1, rel2):
            if rel:
                db.session.delete(rel)
        db.session.commit()