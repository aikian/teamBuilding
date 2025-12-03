"""
Service layer for team operations.

This module contains business logic for creating teams, listing teams
within a class or category, applying to join a team, and managing
applications. It is a simplified implementation that covers core
functionality required by the project specification.
"""

from typing import List

from database import db
from models.team import Team
from models.team_member import TeamMember
from models.team_application import TeamApplication
from models.user import User


class TeamService:
    """Encapsulates team-related business rules."""

    @staticmethod
    # 팀 생성
    def create_team(
        owner_id: int,
        name: str,
        goal: str,
        required_skills: str,
        capacity: int,
        class_id: int = None,
        category_id: int = None,
        openchat_url: str | None = None,
    ) -> Team:
    
     #   새로운 팀을 생성하고 생성자를 팀장(LEADER)으로 임명합니다.
    
        team = Team(
            name=name,
            goal=goal,
            required_skills=required_skills,
            capacity=capacity,
            owner_id=owner_id,
            class_id=class_id,
            category_id=category_id,
            openchat_url=openchat_url,
        )
        db.session.add(team)
        db.session.flush()
        #생성자를 리더로 멤버에 추가
        leader = TeamMember(team_id=team.id, user_id=owner_id, role="LEADER")
        db.session.add(leader)
        db.session.commit()
        return team

    @staticmethod
    # 특정 클래스에 속한 팀 목록을 반환
    def list_teams_for_class(class_id: int) -> List[Team]:
        """Return all teams associated with a given class."""
        return Team.query.filter_by(class_id=class_id).all()

    @staticmethod
    # 특정 카테고리에 속한 팀 목록을 반환
    def list_teams_for_category(category_id: int) -> List[Team]:
        """Return all teams associated with a given category."""
        return Team.query.filter_by(category_id=category_id).all()

    @staticmethod
    # 가입신청
    def apply_to_team(team_id: int, user_id: int, message: str = None) -> TeamApplication:
        """Submit an application to join a team."""
        # 1. 이미 멤버인지 체크
        if TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first():
            raise ValueError("이미 팀 멤버입니다.")
        # 2. 이미 가입신청을 했는지 체크
        if TeamApplication.query.filter_by(team_id=team_id, user_id=user_id).first():
            raise ValueError("이미 지원했습니다.")
        application = TeamApplication(team_id=team_id, user_id=user_id, message=message)
        db.session.add(application)
        db.session.commit()
        return application

    @staticmethod
    # 가입신청 수락/거절
    def process_application(application_id: int, accept: bool) -> None:
        """Accept or reject a team application."""
        app = TeamApplication.query.get(application_id)
        if not app or app.status != "PENDING":
            return
        app.status = "ACCEPTED" if accept else "REJECTED"
        app.decided_at = db.func.now()
        if accept:
            # 수락 시 팀 정원 체크
            team = Team.query.get(app.team_id)
            if team.capacity is not None:
                current_members = TeamMember.query.filter_by(team_id=team.id).count()
                if current_members >= team.capacity:
                    # 정원이 찼으면 거절 처리
                    app.status = "REJECTED"
                else:
                    # 정원이 차지 않았다면 등록
                    member = TeamMember(team_id=app.team_id, user_id=app.user_id, role="MEMBER")
                    db.session.add(member)
        db.session.commit()

    @staticmethod
    # 팀 초대
    def invite_user(team_id: int, from_user_id: int, to_user_id: int) -> None:
        """Send an invitation from the team leader to another user."""
        from models.team_invitation import TeamInvitation
        #이미 멤버인지 확인
        if TeamMember.query.filter_by(team_id=team_id, user_id=to_user_id).first():
            raise ValueError("이미 팀 멤버입니다.")
        existing_invite = TeamInvitation.query.filter_by(team_id=team_id, to_user_id=to_user_id, status="PENDING").first()
        #이미 대기 중인 초대가 있는지 확인
        if existing_invite:
            raise ValueError("이미 초대되었습니다.")
        invitation = TeamInvitation(team_id=team_id, from_user_id=from_user_id, to_user_id=to_user_id)
        db.session.add(invitation)
        # 초대받은 유저에게 알림 전송
        from services.notification_service import NotificationService
        NotificationService.send_notification(to_user_id, "INVITATION", f"팀 초대가 도착했습니다.", related_id=invitation.id)
        db.session.commit()

    @staticmethod
    # 팀 초대 수락/거절
    def process_invitation(invitation_id: int, accept: bool, current_user_id: int) -> None:
        """Accept or reject an invitation."""
        from models.team_invitation import TeamInvitation
        invitation = TeamInvitation.query.get(invitation_id)
        if not invitation or invitation.status != "PENDING" or invitation.to_user_id != current_user_id:
            return
        invitation.status = "ACCEPTED" if accept else "REJECTED"
        invitation.responded_at = db.func.now()
        from services.notification_service import NotificationService
        if accept:
            # 수락 시 정원 체크
            team = Team.query.get(invitation.team_id)
            if team.capacity is not None:
                current_members = TeamMember.query.filter_by(team_id=team.id).count()
                # 정원 초과 시 거절 처리/리더에게 알림
                if current_members >= team.capacity:
                    invitation.status = "REJECTED"
                    NotificationService.send_notification(invitation.from_user_id, "INVITATION_REJECTED", f"정원이 초과되어 초대가 거절되었습니다.", related_id=invitation.id)
                # 멤버 추가 및 알림
                else:
                    member = TeamMember(team_id=team.id, user_id=current_user_id, role="MEMBER")
                    db.session.add(member)
                    NotificationService.send_notification(invitation.from_user_id, "INVITATION_ACCEPTED", f"{current_user_id} 님이 초대를 수락했습니다.", related_id=invitation.id)
            else: # 정원 제한이 없는 경우
                member = TeamMember(team_id=team.id, user_id=current_user_id, role="MEMBER")
                db.session.add(member)
                NotificationService.send_notification(invitation.from_user_id, "INVITATION_ACCEPTED", f"{current_user_id} 님이 초대를 수락했습니다.", related_id=invitation.id)
        else: # 거절 시 알림
            NotificationService.send_notification(invitation.from_user_id, "INVITATION_REJECTED", f"{current_user_id} 님이 초대를 거절했습니다.", related_id=invitation.id)
        db.session.commit()

    @staticmethod
    # 팀원 삭제
    def remove_member(team_id: int, user_id: int, by_user_id: int) -> None:
        """Remove a member from the team if requested by the leader or by the member themself."""
        team = Team.query.get(team_id)
        if not team:
            return
        # 삭제 대상 조회
        membership = TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first()
        if not membership:
            return
        # 삭제 요청자 권한 조회
        actor_member = TeamMember.query.filter_by(team_id=team_id, user_id=by_user_id).first()
        if not actor_member:
            return
        # 본인이 아니면서 팀장도 아닌 경우 삭제 불가
        if user_id != by_user_id and actor_member.role != "LEADER":
            raise ValueError("팀원을 제거할 권한이 없습니다.")
        # 예외: 팀장은 스스로 탈퇴 불가
        if membership.role == "LEADER" and user_id == by_user_id:
            raise ValueError("팀장은 본인을 제거할 수 없습니다. 위임 후 탈퇴하세요.")
        # 멤버 삭제 수행
        db.session.delete(membership)
        from services.notification_service import NotificationService
        # 알림 전송
        if user_id != by_user_id:
            NotificationService.send_notification(user_id, "REMOVED", f"팀에서 추방되었습니다.", related_id=team_id)
        else:
            NotificationService.send_notification(team.owner_id, "WITHDRAWAL", f"팀원이 탈퇴했습니다.", related_id=team_id)
        db.session.commit()

    @staticmethod
    # 팀장 권한 위임
    def delegate_leader(team_id: int, new_leader_id: int, by_user_id: int) -> None:
        """Delegate leader role to another member."""
        team = Team.query.get(team_id)
        if not team:
            return
        # 현재 리더와 새 리더 조회
        current_leader_member = TeamMember.query.filter_by(team_id=team_id, user_id=by_user_id, role="LEADER").first()
        new_leader_member = TeamMember.query.filter_by(team_id=team_id, user_id=new_leader_id).first()
        if not current_leader_member or not new_leader_member:
            raise ValueError("권한을 위임할 수 없습니다.")
        # 역할 교체
        current_leader_member.role = "MEMBER"
        new_leader_member.role = "LEADER"
        # 팀 리더 정보 업데이트
        team.owner_id = new_leader_id
        from services.notification_service import NotificationService
        NotificationService.send_notification(new_leader_id, "DELEGATED", "팀장 권한이 위임되었습니다.", related_id=team_id)
        db.session.commit()

    @staticmethod
    # 팀 해체
    def dissolve_team(team_id: int, by_user_id: int) -> None:
        """Dissolve a team and notify all members."""
        team = Team.query.get(team_id)
        if not team:
            return
        # 팀장만 해체 가능
        if team.owner_id != by_user_id:
            raise ValueError("팀을 해체할 권한이 없습니다.")
        from services.notification_service import NotificationService
        # 멤버들에게 알림 전송
        members = TeamMember.query.filter_by(team_id=team_id).all()
        for mem in members:
            if mem.user_id != by_user_id:
                NotificationService.send_notification(mem.user_id, "TEAM_DISSOLVED", f"팀이 해체되었습니다.", related_id=team_id)
        # 팀 삭제
        db.session.delete(team)
        db.session.commit()

    @staticmethod
    # 팀 모집상태 변경
    def update_recruit_status(team_id: int, status: str, by_user_id: int) -> None:
        """Open or close recruitment for a team."""
        team = Team.query.get(team_id)
        if not team or team.owner_id != by_user_id:
            raise ValueError("권한이 없습니다.")
        if status not in ("OPEN", "CLOSED"):
            raise ValueError("잘못된 상태입니다.")
        team.recruit_status = status
        db.session.commit()