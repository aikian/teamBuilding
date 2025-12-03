"""
매칭 기능 블루프린트

- 특정 팀에 적합한 후보 사용자 목록 계산 및 표시
- MatchingService를 이용하여 점수를 계산하고 후보자를 정렬
- 팀 리더 여부 확인 후 템플릿에서 권한 표시
"""

from flask import Blueprint, render_template

from services.matching_service import MatchingService
from models.team import Team
from models.user import User

matching_bp = Blueprint("matching", __name__)

# ----------------------------
# /<team_id>
# 팀 후보자 매칭 결과 페이지
# ----------------------------
@matching_bp.route("/<int:team_id>")
def match(team_id: int):
    """
    팀 후보자 목록을 매칭 점수 기준으로 정렬하여 보여줌

    1. team_id로 팀 조회, 없으면 404 처리
    2. 현재 팀에 속하지 않은 사용자 목록 조회
    3. MatchingService를 통해 후보자 점수 계산
    4. 현재 로그인 사용자가 팀 리더인지 확인
    5. 템플릿에 팀 정보, 후보자 목록, 리더 여부 전달
    """
    # 1. 팀 정보 가져오기
    team = Team.query.get_or_404(team_id)

    # 2. 현재 팀 멤버 ID 리스트 가져오기
    from models.team_member import TeamMember
    member_ids = [m.user_id for m in TeamMember.query.filter_by(team_id=team_id).all()]

    # 3. 팀에 속하지 않은 사용자 목록 조회
    candidates = User.query.filter(User.id.notin_(member_ids)).all()

    # 4. 후보자 점수 계산 (MatchingService)
    scored_candidates = MatchingService.match_candidates(candidates, team)

    # 5. 현재 로그인 사용자가 팀 리더인지 확인
    from flask import session
    current_user_id = session.get("user_id")
    is_leader = current_user_id == team.owner_id

    # 6. 매칭 결과 템플릿 렌더링
    return render_template(
        "matching_results.html",
        team=team,
        candidates=scored_candidates,
        is_leader=is_leader
    )
