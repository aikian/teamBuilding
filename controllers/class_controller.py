"""
클래스 관련 기능을 담당하는 블루프린트입니다.

이 블루프린트는 클래스 생성, 사용자가 속한 클래스 목록 조회,
고유 코드를 통한 클래스 참여를 처리합니다. 핵심 비즈니스 로직은
``class_service``에 위임됩니다.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.class_service import ClassService
from services.team_service import TeamService
from models.class_ import ClassRoom  # noqa: F401 imported for type reference


class_bp = Blueprint("class", __name__)


@class_bp.route("/")
def list_classes() -> str:
    """
    현재 사용자가 가입한 모든 클래스를 표시합니다.

    로그인되어 있지 않은 경우 빈 목록이 반환됩니다.
    """
    current_user_id = session.get("user_id")
    classes = ClassService.get_classes_for_user(current_user_id) if current_user_id else []
    return render_template("class_list.html", classes=classes)


@class_bp.route("/create", methods=["GET", "POST"])
def create() -> str:
    """
    클래스 생성 페이지를 표시하고 입력된 정보로 새 클래스를 만듭니다.

    POST 요청 시 이름과 설명을 받아 현재 사용자를 대표자로 클래스
    레코드를 생성하고 클래스 목록 페이지로 이동합니다. 로그인하지
    않았다면 로그인 페이지로 리다이렉트합니다.
    """
    if request.method == "POST":
        if not session.get("user_id"):
            flash("로그인이 필요합니다.")
            return redirect(url_for("user.login"))
        ClassService.create_class(
            owner_id=session["user_id"],
            name=request.form["name"],
            description=request.form.get("description"),
        )
        return redirect(url_for("class.list_classes"))
    return render_template("class_create.html")


@class_bp.route("/join", methods=["POST"])
def join() -> str:
    """
    고유 코드를 이용하여 기존 클래스에 참여합니다.

    로그인하지 않은 상태에서 요청하면 로그인 페이지로 리다이렉트하고,
    코드가 유효하면 클래스에 참여하도록 ``class_service``에 요청합니다.
    """
    if not session.get("user_id"):
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    code = request.form.get("code")
    try:
        ClassService.join_class(session["user_id"], code)
        flash("클래스에 참여하였습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(url_for("class.list_classes"))


@class_bp.route("/<int:class_id>")
def detail(class_id: int) -> str:
    """Display a single class and its teams."""
    from flask import request, session   # 추가
    from models.user import User         # 추가

    clazz = ClassRoom.query.get_or_404(class_id)
    teams = TeamService.list_teams_for_class(class_id)
    
    # 정렬 모드
    sort_mode = request.args.get("sort")

    if sort_mode == "match":
        user_id = session.get("user_id")

        if user_id:
            user = User.query.get(user_id)
            profile = getattr(user, "profile", None)

            # 사용자 태그(성격, 목표, 기술)
            user_tags = []
            if profile:
                for field in ("personality", "goals", "skills"):
                    value = getattr(profile, field, None)
                    if value:
                        user_tags.extend(
                            [t.strip().lower() for t in value.split(",") if t.strip()]
                        )

            def calc_match_score(team):
                if not user_tags or not team.required_skills:
                    return 0
                team_tags = [
                    t.strip().lower()
                    for t in team.required_skills.split(",")
                    if t.strip()
                ]
                return len(set(user_tags) & set(team_tags))

            teams = sorted(
                teams,
                key=lambda t: (calc_match_score(t), t.id),
                reverse=True,
            )
    # 여기까지 정렬 관련
    
    # 수정
    return render_template("class_detail.html", clazz=clazz, class_room=clazz, teams=teams)