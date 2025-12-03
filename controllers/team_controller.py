"""
팀 기능을 담당하는 블루프린트입니다.

팀 생성, 팀 목록 조회, 팀 지원 및 신청 처리 등과 관련된 라우트를 정의합니다.
비즈니스 로직은 ``TeamService``에 위임됩니다.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.team_service import TeamService
from services.class_service import ClassService
from services.category_service import CategoryService

team_bp = Blueprint("team", __name__)


@team_bp.route("/create", methods=["GET", "POST"])
def create_team():
    """Display form to create a new team and handle submission."""
    if request.method == "POST":
        if not session.get("user_id"):
            flash("로그인이 필요합니다.")
            return redirect(url_for("user.login"))
        name = request.form["name"]
        goal = request.form.get("goal")
        required_skills = request.form.get("required_skills")
        capacity = int(request.form.get("capacity")) if request.form.get("capacity") else None
        class_id = request.form.get("class_id")
        category_id = request.form.get("category_id")
        openchat_url = request.form.get("openchat_url") or None
        # Convert empty strings to None
        class_id = int(class_id) if class_id else None
        category_id = int(category_id) if category_id else None
        TeamService.create_team(
            owner_id=session["user_id"],
            name=name,
            goal=goal,
            required_skills=required_skills,
            capacity=capacity,
            class_id=class_id,
            category_id=category_id,
            openchat_url=openchat_url,
        )
        return redirect(url_for("team.list_my_teams"))
    # For the form we need classes and categories lists
    user_id = session.get("user_id")
    classes = ClassService.get_classes_for_user(user_id) if user_id else []
    categories = CategoryService.list_categories()
    default_class_id = request.args.get("class_id", type=int)
    default_category_id = request.args.get("category_id", type=int)
    return render_template(
        "team_create.html",
        classes=classes,
        categories=categories,
        default_class_id=default_class_id,
        default_category_id=default_category_id,
    )


@team_bp.route("/my")
def list_my_teams():
    """List teams for the current user's classes and categories."""
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    # For simplicity we list all teams the user is a member of
    from models.team_member import TeamMember
    from models.team import Team
    memberships = TeamMember.query.filter_by(user_id=user_id).all()
    team_ids = [m.team_id for m in memberships]
    teams = Team.query.filter(Team.id.in_(team_ids)).all() if team_ids else []
    return render_template("team_list.html", teams=teams)


@team_bp.route("/<int:team_id>")
def team_detail(team_id: int):
    """Show details of a team and its members."""
    from models.team import Team
    from models.team_member import TeamMember
    team = Team.query.get_or_404(team_id)
    memberships = TeamMember.query.filter_by(team_id=team_id).all()
    # Build list of member dict with user info
    from models.user import User
    members = []
    for mem in memberships:
        user = User.query.get(mem.user_id)
        members.append({'member': mem, 'user': user})
    current_user_id = session.get("user_id")
    # Determine if leader
    is_leader = current_user_id == team.owner_id
    # Pending applications
    from models.team_application import TeamApplication
    applications = []
    # Pending invitations for leader to view
    from models.team_invitation import TeamInvitation
    invitations = []
    if is_leader:
        invs = TeamInvitation.query.filter_by(team_id=team_id, status="PENDING").all()
        # Build list with user info
        from models.user import User
        for inv in invs:
            user = User.query.get(inv.to_user_id)
            invitations.append({'invitation': inv, 'user': user})
        pending_apps = TeamApplication.query.filter_by(team_id=team_id, status="PENDING").all()
        for app in pending_apps:
            user = User.query.get(app.user_id)
            applications.append({'application': app, 'user': user})
    # Determine membership and pending application/invite for current user
    user_member = None
    user_pending_application = None
    user_pending_invite = None
    if current_user_id:
        user_member = TeamMember.query.filter_by(team_id=team_id, user_id=current_user_id).first()
        user_pending_application = TeamApplication.query.filter_by(team_id=team_id, user_id=current_user_id, status="PENDING").first()
        user_pending_invite = TeamInvitation.query.filter_by(team_id=team_id, to_user_id=current_user_id, status="PENDING").first()
    return render_template(
        "team_detail.html",
        team=team,
        members=members,
        is_leader=is_leader,
        applications=applications,
        invitations=invitations,
        user_member=user_member,
        user_pending_application=user_pending_application,
        user_pending_invite=user_pending_invite,
    )


@team_bp.route("/apply/<int:team_id>", methods=["POST"])
def apply_to_team(team_id: int):
    """Apply to join a team."""
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    message = request.form.get("message")
    try:
        TeamService.apply_to_team(team_id, user_id, message)
        flash("팀에 지원했습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(url_for("team.team_detail", team_id=team_id))


@team_bp.route("/application/<int:application_id>/<string:action>", methods=["POST"])
def process_application(application_id: int, action: str):
    """Accept or reject a team application."""
    accept = action == "accept"
    TeamService.process_application(application_id, accept)
    return redirect(request.referrer or url_for("team.list_my_teams"))


# --- New management and invitation routes ---

@team_bp.route("/invite/<int:team_id>/<int:user_id>", methods=["POST"])
def invite_user(team_id: int, user_id: int):
    """Send an invitation to a user to join the team."""
    current_user_id = session.get("user_id")
    if not current_user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    try:
        TeamService.invite_user(team_id, current_user_id, user_id)
        flash("초대가 전송되었습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(request.referrer or url_for("team.team_detail", team_id=team_id))


@team_bp.route("/invitation/<int:invitation_id>/<string:action>", methods=["POST"])
def process_invitation(invitation_id: int, action: str):
    """Accept or reject a team invitation."""
    current_user_id = session.get("user_id")
    if not current_user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    accept = action == "accept"
    TeamService.process_invitation(invitation_id, accept, current_user_id)
    return redirect(request.referrer or url_for("notification.list_notifications"))

# 수정
@team_bp.route("/remove/<int:team_id>/<int:user_id>", methods=["POST"])
def remove_member(team_id: int, user_id: int):
    """Remove a member from a team."""
    current_user_id = session.get("user_id")
    try:
        TeamService.remove_member(team_id, user_id, current_user_id)
        # 누가 요청했는지에 따라 다른 문구
        if current_user_id == user_id:
            # 본인이 자기 자신을 제거 → 자발적 탈퇴
            flash("팀을 탈퇴했습니다.")
        else:
            # 팀장이 다른 사람을 제거 → 강퇴
            flash("팀원이 제거했습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(request.referrer or url_for("team.team_detail", team_id=team_id))


@team_bp.route("/delegate/<int:team_id>/<int:user_id>", methods=["POST"])
def delegate_leader(team_id: int, user_id: int):
    """Delegate team leader role to another member."""
    current_user_id = session.get("user_id")
    try:
        TeamService.delegate_leader(team_id, user_id, current_user_id)
        flash("팀장 권한이 위임되었습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(request.referrer or url_for("team.team_detail", team_id=team_id))


@team_bp.route("/dissolve/<int:team_id>", methods=["POST"])
def dissolve_team(team_id: int):
    """Dissolve a team."""
    current_user_id = session.get("user_id")
    try:
        TeamService.dissolve_team(team_id, current_user_id)
        flash("팀이 해체되었습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(url_for("team.list_my_teams"))


@team_bp.route("/recruit/<int:team_id>/<string:status>", methods=["POST"])
def update_recruit_status(team_id: int, status: str):
    """Open or close recruitment for a team."""
    current_user_id = session.get("user_id")
    try:
        TeamService.update_recruit_status(team_id, status.upper(), current_user_id)
        flash("모집 상태가 변경되었습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(request.referrer or url_for("team.team_detail", team_id=team_id))


# 추가 코드
@team_bp.route("/<int:team_id>/edit", methods=["GET", "POST"])
def edit_team(team_id: int):
    """팀 정보를 수정하는 페이지 (팀장 전용)."""
    from models.team import Team

    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))

    team = Team.query.get_or_404(team_id)

    # 팀장인지 확인
    if team.owner_id != user_id:
        flash("팀장만 팀 정보를 수정할 수 있습니다.")
        return redirect(url_for("team.team_detail", team_id=team_id))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        goal = request.form.get("goal") or None
        required_skills = request.form.get("required_skills") or None
        capacity_raw = request.form.get("capacity")
        capacity = int(capacity_raw) if capacity_raw else None
        openchat_url = request.form.get("openchat_url") or None

        if not name:
            flash("팀 이름은 필수입니다.")
            return redirect(url_for("team.edit_team", team_id=team_id))

        # 여기서 TeamService 써도 되고, 직접 업데이트해도 됨
        team.name = name
        team.goal = goal
        team.required_skills = required_skills
        team.capacity = capacity
        team.openchat_url = openchat_url

        from database import db
        db.session.commit()

        flash("팀 정보가 수정되었습니다.")
        return redirect(url_for("team.team_detail", team_id=team_id))

    # GET 요청: 수정 폼 렌더링
    return render_template("team_edit.html", team=team)
