"""
카테고리 기능을 담당하는 블루프린트입니다.

카테고리를 생성하고 목록을 조회하는 라우트를 제공합니다. 팀을 카테고리와
연결하여 관심사 기반 팀 빌딩이 가능하도록 합니다.
"""

from flask import Blueprint, render_template, request, session, flash

from services.category_service import CategoryService
from services.team_service import TeamService
from models.category import Category
from services.team_service import TeamService

category_bp = Blueprint("category", __name__)


@category_bp.route("/", methods=["GET", "POST"])
def list_and_create():
    """
    카테고리 목록을 표시하고 새 카테고리를 생성합니다.

    POST 요청 시 이름을 받아 카테고리를 만들며, GET 요청 시 전체 목록을
    반환합니다.
    """
    if request.method == "POST":
        name = request.form.get("name")
        try:
            CategoryService.create_category(name=name, created_by=session.get("user_id"))
            flash("카테고리가 추가되었습니다.")
        except Exception as exc:
            flash(str(exc))
    categories = CategoryService.list_categories()
    return render_template("category_list.html", categories=categories)

# 수정 (정렬 기능)
@category_bp.route("/<int:category_id>")
def detail(category_id: int):
    """Display category detail with its teams."""
    from flask import request, session
    from models.user import User

    category = Category.query.get_or_404(category_id)
    teams = TeamService.list_teams_for_category(category_id)

    # 정렬 기준 파라미터 (없으면 기본 정렬)
    sort_mode = request.args.get("sort", "default")

    if sort_mode == "match":
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            profile = getattr(user, "profile", None)

            # 사용자 태그(성격, 목표, 기술)를 한 번에 모아두기
            user_tags: list[str] = []
            if profile:
                for field in ("personality", "goals", "skills"):
                    value = getattr(profile, field, None)
                    if value:
                        user_tags.extend(
                            [t.strip().lower() for t in value.split(",") if t.strip()]
                        )

            def calc_match_score(team):
                """사용자 태그와 팀 필요 역량(required_skills)의 교집합 개수로 점수 계산."""
                if not user_tags or not team.required_skills:
                    return 0
                team_tags = [
                    t.strip().lower()
                    for t in team.required_skills.split(",")
                    if t.strip()
                ]
                return len(set(user_tags) & set(team_tags))

            # 점수 높은 순 → 동점이면 id 큰 순으로
            teams = sorted(
                teams,
                key=lambda t: (calc_match_score(t), t.id),
                reverse=True,
            )

    return render_template(
        "category_detail.html",
        category=category,
        teams=teams,
        sort_mode=sort_mode,  # 템플릿에서 현재 정렬 기준 표시용
    )

