"""
팀 관련 비즈니스 로직을 제공하는 서비스 레이어입니다.

팀 생성, 클래스/카테고리 내 팀 목록 조회, 가입 신청 및 처리,
팀 초대, 팀원 관리, 팀장 권한 위임, 팀 해체, 모집 상태 변경 등
프로젝트 핵심 기능과 확장 기능을 포함합니다.
"""

from typing import List

from database import db
from models.team import Team
from models.team_member import TeamMember
from models.team_application import TeamApplication
from models.user import User
from models.category import Category
from models.class_ import ClassRoom


class TeamService:
    """Encapsulates team-related business rules."""

    # =================================
    # 🔹 팀 타입 라벨 가져오기 (클래스 / 카테고리)
    # =================================
    @staticmethod
    def get_team_type_label(team: Team) -> str:
        """Return '클래스: name', '카테고리: name', or just team name if neither."""
        if team.class_id:
            cls = ClassRoom.query.get(team.class_id)
            if cls:
                return f"클래스: {cls.name}"
        if team.category_id:
            cat = Category.query.get(team.category_id)
            if cat:
                return f"카테고리: {cat.name}"
        return f"{team.name}"

    # =================================
    # 팀 생성
    # =================================
    @staticmethod
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
        # 생성자를 리더로 멤버에 추가
        leader = TeamMember(team_id=team.id, user_id=owner_id, role="LEADER")
        db.session.add(leader)
        db.session.commit()
        return team

    # =================================
    # 클래스 / 카테고리 팀 조회
    # =================================
    @staticmethod
    def list_teams_for_class(class_id: int) -> List[Team]:
        return Team.query.filter_by(class_id=class_id).all()

    @staticmethod
    def list_teams_for_category(category_id: int) -> List[Team]:
        return Team.query.filter_by(category_id=category_id).all()

    # =================================
    # 가입 신청
    # =================================
    @staticmethod
    def apply_to_team(team_id: int, user_id: int, message: str = None) -> TeamApplication:
        if TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first():
            raise ValueError("이미 팀 멤버입니다.")
        if TeamApplication.query.filter_by(team_id=team_id, user_id=user_id).first():
            raise ValueError("이미 지원했습니다.")
        application = TeamApplication(team_id=team_id, user_id=user_id, message=message)
        db.session.add(application)
        db.session.commit()
        return application

    @staticmethod
    def process_application(application_id: int, accept: bool) -> None:
        app = TeamApplication.query.get(application_id)
        if not app or app.status != "PENDING":
            return

        team = Team.query.get(app.team_id)
        if not team:
            return

        from services.notification_service import NotificationService

        team_label = TeamService.get_team_type_label(team)

        # 1) 거절
        if not accept:
            app.status = "REJECTED"
            app.decided_at = db.func.now()
            NotificationService.send_notification(
                app.user_id,
                "APPLICATION_REJECTED",
                f"[{team_label}] 팀 지원이 거절되었습니다.",
                related_id=team.id,
            )
            db.session.commit()
            return

        # 2) 승인인데 정원 체크
        if team.capacity is not None:
            current_members = TeamMember.query.filter_by(team_id=team.id).count()
            if current_members >= team.capacity:
                app.status = "REJECTED"
                app.decided_at = db.func.now()
                NotificationService.send_notification(
                    app.user_id,
                    "APPLICATION_REJECTED",
                    f"[{team_label}] 팀 정원이 가득 차 지원이 거절되었습니다.",
                    related_id=team.id,
                )
                db.session.commit()
                return

        # 3) 승인 및 팀원 추가
        member = TeamMember(team_id=team.id, user_id=app.user_id, role="MEMBER")
        db.session.add(member)

        app.status = "ACCEPTED"
        app.decided_at = db.func.now()

        NotificationService.send_notification(
            app.user_id,
            "APPLICATION_ACCEPTED",
            f"[{team_label}] 팀 지원이 승인되었습니다.",
            related_id=team.id,
        )

        db.session.commit()

    # =================================
    # 팀 초대
    # =================================
    @staticmethod
    def invite_user(team_id: int, from_user_id: int, to_user_id: int) -> None:
        from models.team_invitation import TeamInvitation
        from services.class_service import ClassService

        team = Team.query.get(team_id)
        if not team:
            raise ValueError("존재하지 않는 팀입니다.")

        if team.class_id:
            user_classes = ClassService.get_classes_for_user(to_user_id) or []
            user_class_ids = {c.id for c in user_classes}
            if team.class_id not in user_class_ids:
                raise ValueError("해당 수업에 속한 사용자만 초대할 수 있습니다.")

        if TeamMember.query.filter_by(team_id=team_id, user_id=to_user_id).first():
            raise ValueError("이미 팀 멤버입니다.")

        existing_invite = TeamInvitation.query.filter_by(
            team_id=team_id, to_user_id=to_user_id, status="PENDING"
        ).first()
        if existing_invite:
            raise ValueError("이미 초대되었습니다.")

        invitation = TeamInvitation(
            team_id=team_id, from_user_id=from_user_id, to_user_id=to_user_id
        )
        db.session.add(invitation)

        from services.notification_service import NotificationService

        team_label = TeamService.get_team_type_label(team)
        NotificationService.send_notification(
            to_user_id,
            "INVITATION",
            f"[{team_label}] {team.name}팀에서 초대가 도착했습니다.",
            related_id=invitation.id,
        )

        db.session.commit()

    @staticmethod
    def process_invitation(invitation_id: int, accept: bool, current_user_id: int) -> None:
        from models.team_invitation import TeamInvitation
        from services.notification_service import NotificationService

        invitation = TeamInvitation.query.get(invitation_id)
        if not invitation or invitation.status != "PENDING" or invitation.to_user_id != current_user_id:
            return

        team = Team.query.get(invitation.team_id)
        team_label = TeamService.get_team_type_label(team)

        user = User.query.get(current_user_id)
        user_name = user.name if user else f"사용자 {current_user_id}"

        invitation.status = "ACCEPTED" if accept else "REJECTED"
        invitation.responded_at = db.func.now()

        if accept:
            if team.capacity is not None:
                current_members = TeamMember.query.filter_by(team_id=team.id).count()
                if current_members >= team.capacity:
                    invitation.status = "REJECTED"
                    NotificationService.send_notification(
                        invitation.from_user_id,
                        "INVITATION_REJECTED",
                        f"[{team_label}] 팀 정원이 가득 차 초대가 거절되었습니다.",
                        related_id=invitation.id,
                    )
                    raise ValueError("정원이 모두 차 가입하지 못했습니다.")
                else:
                    member = TeamMember(team_id=team.id, user_id=current_user_id, role="MEMBER")
                    db.session.add(member)
                    NotificationService.send_notification(
                        invitation.from_user_id,
                        "INVITATION_ACCEPTED",
                        f"[{team_label}] 팀에 {user_name} 님이 초대를 수락했습니다.",
                        related_id=invitation.id,
                    )
            else:
                member = TeamMember(team_id=team.id, user_id=current_user_id, role="MEMBER")
                db.session.add(member)
                NotificationService.send_notification(
                    invitation.from_user_id,
                    "INVITATION_ACCEPTED",
                    f"[{team_label}] 팀에 {user_name} 님이 초대를 수락했습니다.",
                    related_id=invitation.id,
                )
        else:
            NotificationService.send_notification(
                invitation.from_user_id,
                "INVITATION_REJECTED",
                f"[{team_label}] 팀 초대를 {user_name} 님이 거절했습니다.",
                related_id=invitation.id,
            )

        db.session.commit()

    # =================================
    # 팀원 삭제
    # =================================
    @staticmethod
    def remove_member(team_id: int, user_id: int, by_user_id: int) -> None:
        team = Team.query.get(team_id)
        if not team:
            return

        membership = TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first()
        if not membership:
            return

        actor_member = TeamMember.query.filter_by(team_id=team_id, user_id=by_user_id).first()
        if not actor_member:
            return

        if user_id != by_user_id and actor_member.role != "LEADER":
            raise ValueError("팀원을 제거할 권한이 없습니다.")
        if membership.role == "LEADER" and user_id == by_user_id:
            raise ValueError("팀장은 본인을 제거할 수 없습니다. 위임 후 탈퇴하세요.")

        db.session.delete(membership)

        from services.notification_service import NotificationService
        team_label = TeamService.get_team_type_label(team)

        if user_id != by_user_id:
            NotificationService.send_notification(
                user_id, "REMOVED", f"[{team_label}] 팀에서 추방되었습니다.", related_id=team_id
            )
        else:
            NotificationService.send_notification(
                team.owner_id, "WITHDRAWAL", f"[{team_label}] 팀에서 {User.query.get(user_id).name} 님이 탈퇴했습니다.", related_id=team_id
            )

        db.session.commit()

    # =================================
    # 팀장 권한 위임
    # =================================
    @staticmethod
    def delegate_leader(team_id: int, new_leader_id: int, by_user_id: int) -> None:
        team = Team.query.get(team_id)
        if not team:
            return

        current_leader_member = TeamMember.query.filter_by(team_id=team_id, user_id=by_user_id, role="LEADER").first()
        new_leader_member = TeamMember.query.filter_by(team_id=team_id, user_id=new_leader_id).first()
        if not current_leader_member or not new_leader_member:
            raise ValueError("권한을 위임할 수 없습니다.")

        current_leader_member.role = "MEMBER"
        new_leader_member.role = "LEADER"
        team.owner_id = new_leader_id

        from services.notification_service import NotificationService
        NotificationService.send_notification(new_leader_id, "DELEGATED", "팀장 권한이 위임되었습니다.", related_id=team_id)

        db.session.commit()

    # =================================
    # 팀 해체
    # =================================
    @staticmethod
    def dissolve_team(team_id: int, by_user_id: int) -> None:
        team = Team.query.get(team_id)
        if not team:
            return
        if team.owner_id != by_user_id:
            raise ValueError("팀을 해체할 권한이 없습니다.")

        from services.notification_service import NotificationService
        members = TeamMember.query.filter_by(team_id=team_id).all()
        team_label = TeamService.get_team_type_label(team)
        for mem in members:
            if mem.user_id != by_user_id:
                NotificationService.send_notification(
                    mem.user_id, "TEAM_DISSOLVED", f"[{team_label}] 팀이 해체되었습니다.", related_id=team_id
                )

        db.session.delete(team)
        db.session.commit()

    # =================================
    # 팀 모집 상태 변경
    # =================================
    @staticmethod
    def update_recruit_status(team_id: int, status: str, by_user_id: int) -> None:
        team = Team.query.get(team_id)
        if not team or team.owner_id != by_user_id:
            raise ValueError("권한이 없습니다.")
        if status not in ("OPEN", "CLOSED"):
            raise ValueError("잘못된 상태입니다.")
        team.recruit_status = status
        db.session.commit()
