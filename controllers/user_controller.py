"""
사용자 기능 블루프린트

- 회원가입, 로그인, 로그아웃, 마이페이지 조회/수정/탈퇴 등
- 핵심 로직은 UserService에 위임
- Flask 세션을 통해 로그인 상태 관리
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.user_service import UserService
from models.user import User
from models.team_member import TeamMember

# Blueprint 정의
user_bp = Blueprint("user", __name__)

# ----------------------------
# /register
# 회원가입
# ----------------------------
@user_bp.route("/register", methods=["GET", "POST"])
def register() -> str:
    """
    회원가입 폼 표시 및 신규 사용자 생성

    - GET: 회원가입 화면 반환
    - POST: form 데이터 기반으로 사용자 생성 후 로그인 페이지로 리다이렉트
    - 성공/실패 시 flash 메시지 표시
    - TEST: 올바른/잘못된 입력 처리 확인
    """
    if request.method == "POST":
        try:
            UserService.create_user(
                username=request.form["username"],
                password=request.form["password"],
                name=request.form.get("name"),
                student_no=request.form.get("student_no"),
                school=request.form.get("school"),
                personality=request.form.get("personality"),
                goals=request.form.get("goals"),
                skills=request.form.get("skills"),
            )
            flash("회원가입이 완료되었습니다. 이제 로그인하세요.")
            return redirect(url_for("user.login"))
        except Exception as exc:
            flash(str(exc))
    return render_template("register.html")


# ----------------------------
# /login
# 로그인
# ----------------------------
@user_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    """
    사용자 로그인 처리

    - POST: 아이디/비밀번호 검증 후 세션에 user_id 저장
    - 로그인 성공 시 홈 페이지로, 실패 시 오류 메시지 표시
    - TEST: 올바른/잘못된 로그인 시 플로우 확인
    """
    if request.method == "POST":
        user = UserService.verify_user(
            username=request.form["username"],
            password=request.form["password"],
        )
        if user:
            session["user_id"] = user.id
            flash("로그인 성공!")
            return redirect(url_for("index"))
        flash("ID 또는 비밀번호가 잘못되었습니다.")
    return render_template("login.html")


# ----------------------------
# /logout
# 로그아웃
# ----------------------------
@user_bp.route("/logout")
def logout() -> str:
    """
    세션 초기화 및 로그아웃 처리

    - 로그아웃 후 메인 페이지로 리다이렉트
    - TEST: 세션 초기화 여부 확인
    """
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for("index"))


# ----------------------------
# /mypage
# 마이페이지 조회
# ----------------------------
@user_bp.route("/mypage")
def mypage() -> str:
    """
    마이페이지 렌더링

    - 현재 로그인한 사용자 정보 조회
    - 사용자가 속한 팀 멤버십 조회
    - 팀에서 리더일 경우, 다른 멤버 존재 여부 확인
    - 클래스에서 대표일 경우, 해체 필요 표시
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))

    # 사용자 정보 조회
    user = User.query.get(user_id)

    # 팀 멤버십 조회
    teams = TeamMember.query.filter_by(user_id=user_id).all()

    # 리더인 팀 중 다른 멤버 존재 여부 확인
    leader_conflicts: list[dict] = []

    for membership in teams:
        if membership.role == "LEADER":
            others = TeamMember.query.filter(
                TeamMember.team_id == membership.team_id,
                TeamMember.user_id != user_id,
            ).count()
            leader_conflicts.append(
                {
                    "team": membership.team,
                    "has_other_members": others > 0,
                    "class_room": None  # 팀 관련이므로 클래스는 None
                }
            )

    # 클래스 대표 여부 확인
    # (ClassRoom 모델의 leader_id가 현재 사용자 id와 같다면 대표)
    from models.class_ import ClassRoom  # 클래스 모델 임포트

    class_rooms = ClassRoom.query.filter_by(owner_id=user_id).all()  # owner_id로 수정
    for c in class_rooms:
        leader_conflicts.append(
            {
                "team": None,
                "has_other_members": False,
                "class_room": c
            }
        )

    return render_template("mypage.html", user=user, teams=teams, leader_conflicts=leader_conflicts)



# ----------------------------
# /mypage/update
# 프로필 수정
# ----------------------------
@user_bp.route("/mypage/update", methods=["POST"])
def update_profile() -> str:
    """
    마이페이지에서 사용자 정보 수정 처리

    - 로그인 체크 후 UserService를 통해 업데이트
    - 성공/실패 메시지 flash
    - TEST: 수정 내용 DB 반영 확인
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    try:
        UserService.update_profile(
            user_id=user_id,
            name=request.form.get("name"),
            school=request.form.get("school"),
            personality=request.form.get("personality"),
            goals=request.form.get("goals"),
            skills=request.form.get("skills"),
        )
        flash("회원 정보가 수정되었습니다.")
    except Exception as exc:
        flash(str(exc))
    return redirect(url_for("user.mypage"))


# ----------------------------
# /mypage/delete
# 회원 탈퇴
# ----------------------------
@user_bp.route("/mypage/delete", methods=["POST"])
def delete_account() -> str:
    """
    사용자 계정 삭제 처리

    - 로그인 체크 후 UserService를 통해 계정 삭제
    - 삭제 후 세션 초기화
    - TEST: 계정 삭제 및 세션 초기화 확인
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user.login"))
    try:
        UserService.delete_user(user_id)
    except Exception as exc:
        flash(str(exc))
        return redirect(url_for("user.mypage"))

    session.clear()
    flash("회원 탈퇴가 완료되었습니다.")
    return redirect(url_for("index"))
