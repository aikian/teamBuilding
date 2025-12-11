"""
매칭 기능 블루프린트

- 특정 팀에 적합한 후보 사용자 목록 계산 및 표시
- MatchingService를 이용하여 점수를 계산하고 후보자를 정렬
- 팀 리더 여부 확인 후 템플릿에서 권한 표시
"""

from flask import Blueprint, render_template, session
from models.team import Team
from models.user import User
from models.team_member import TeamMember
from models.class_member import ClassMember
from services.matching_service import MatchingService

matching_bp = Blueprint("matching", __name__)

@matching_bp.route("/<int:team_id>")
def match(team_id: int):
    # 1. 팀 정보 가져오기
    team = Team.query.get_or_404(team_id)

    # 2. 현재 팀 멤버 ID 리스트 가져오기
    member_ids = [m.user_id for m in TeamMember.query.filter_by(team_id=team_id).all()]

    # 3. 후보자 조회
    if team.class_id:  # 팀이 클래스에 속해 있다면
        # 같은 클래스에 속한 사용자만 후보
        candidates = (
            User.query
            .join(ClassMember, ClassMember.user_id == User.id)
            .filter(ClassMember.class_room.has(id=team.class_id))
            .filter(~User.id.in_(member_ids))
            .all()
        )
    else:
        # 클래스가 없으면 모든 사용자 후보, 단 같은 팀 멤버 제외
        candidates = User.query.filter(~User.id.in_(member_ids)).all()
    
    # 4. 후보자 점수 계산
    scored_candidates = MatchingService.match_candidates(candidates, team)

    # 5. 현재 로그인 사용자가 팀 리더인지 확인
    current_user_id = session.get("user_id")
    is_leader = current_user_id == team.owner_id

    # 6. 결과 렌더링
    return render_template(
        "matching_results.html",
        team=team,
        candidates=scored_candidates,
        is_leader=is_leader
    )
