"""
친구 기능을 담당하는 블루프린트입니다.

사용자들 간의 친구 관계를 관리하는 라우트들을 정의합니다. 사용자 검색,
친구 요청 보내기, 친구 요청 수락 및 차단, 친구 목록 조회 등을 지원하며,
핵심 로직은 ``friend_service``에 위임됩니다.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.friend_service import FriendService
from database import db
from models.friend import Friend


friend_bp = Blueprint("friend", __name__)


@friend_bp.route("/search", methods=["GET", "POST"])
def search() -> str:
    """Search for users by name or student number."""
    team_id = request.args.get("team_id", type = int) # 추가 코드
    results = []
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            results = FriendService.search_users(keyword)
    return render_template("friend_search.html", results=results, team_id=team_id) # 수정


@friend_bp.route("/add/<int:user_id>", methods=["POST"])
def add_friend(user_id: int):
    """Send a friend request to another user."""
    current_user_id = session.get("user_id")
    if not current_user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    try:
        FriendService.send_request(current_user_id, user_id)
        flash("친구 요청을 보냈습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(url_for("friend.search"))


@friend_bp.route("/requests")
def pending_requests() -> str:
    """Display pending friend requests for the current user.

    For each pending request we also retrieve the requesting user's
    details so the template can display a friendly name. If the
    requester cannot be found (which should not happen), we simply
    show the user_id.
    """
    user_id = session.get("user_id")
    requests_data: list[dict] = []
    if user_id:
        pending = FriendService.list_pending_requests(user_id)
        # Build a list of dictionaries containing the request and
        # corresponding user object
        from models.user import User
        for req in pending:
            requester = User.query.get(req.user_id)
            requests_data.append({"request": req, "requester": requester})
    return render_template("friend_requests.html", requests=requests_data)


@friend_bp.route("/accept/<int:request_id>", methods=["POST"])
def accept_friend(request_id: int):
    """Accept a pending friend request."""
    current_user_id = session.get("user_id")
    if current_user_id:
        FriendService.accept_request(request_id, current_user_id)
    return redirect(url_for("friend.list_friends"))


@friend_bp.route("/reject/<int:request_id>", methods=["POST"])
def reject_friend(request_id: int):
    """Reject a pending friend request by deleting it."""
    # Only the target user can reject
    current_user_id = session.get("user_id")
    if current_user_id:
        req = Friend.query.get(request_id)
        if req and req.friend_id == current_user_id and req.status == "PENDING":
            # delete both directions if exist
            db.session.delete(req)
            db.session.commit()
    return redirect(url_for("friend.pending_requests"))


@friend_bp.route("/block/<int:user_id>", methods=["POST"])
def block_user(user_id: int):
    """Block a user and prevent future friend requests."""
    current_user_id = session.get("user_id")
    if current_user_id:
        FriendService.block_user(current_user_id, user_id)
    return redirect(url_for("friend.list_friends"))


@friend_bp.route("/remove/<int:user_id>", methods=["POST"])
def remove_friend(user_id: int):
    """Remove a friend relationship (unfriend)."""
    current_user_id = session.get("user_id")
    if current_user_id:
        FriendService.remove_friend(current_user_id, user_id)
    return redirect(url_for("friend.list_friends"))


@friend_bp.route("/list", methods=["GET", "POST"])
def list_friends() -> str:
    """Show the current user's friend list and handle friend requests."""
    current_user_id = session.get("user_id")
    if not current_user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("친구로 추가할 아이디를 입력해주세요.")
        else:
            try:
                FriendService.send_request_by_username(current_user_id, username)
                flash("친구 요청을 보냈습니다.")
            except Exception as exc:
                flash(str(exc))
        return redirect(url_for("friend.list_friends"))

    friends = FriendService.list_friends(current_user_id)
    pending_requests_data: list[dict] = []
    pending = FriendService.list_pending_requests(current_user_id)
    from models.user import User
    for req in pending:
        requester = User.query.get(req.user_id)
        pending_requests_data.append({"request": req, "requester": requester})
    return render_template("friend_list.html", friends=friends, pending_requests=pending_requests_data)