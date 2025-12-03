# 팀 빌딩 지원 웹 애플리케이션

온오프라인 팀 빌딩을 지원하는 웹 애플리케이션입니다. 사용자는 회원가입 시 프로필 정보를 등록하고 이를 바탕으로 팀을 개설하거나 참여할 수 있습니다.

## 주요 기능

- 사용자 계정 관리: 회원가입, 로그인, 로그아웃, 프로필 관리, 회원 탈퇴
- 친구 관리: 아이디로 친구 검색, 친구 요청/수락, 친구 목록 조회
- 클래스 기반 팀 빌딩: 클래스 생성/참여, 클래스 내 팀 생성/지원/관리
- 카테고리 기반 팀 빌딩: 카테고리 생성, 카테고리 내 팀 생성/지원/관리
- 팀 관리: 팀 생성, 모집 관리, 팀원 초대/승인, 팀장 위임, 팀 해체
- 알림 시스템: 친구 요청, 팀 초대, 지원 승인/거절 등 실시간 알림

## 설치 및 실행

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화

애플리케이션을 처음 실행하면 자동으로 데이터베이스 테이블이 생성됩니다.

```bash
python app.py
```

### 3. 서버 실행

```bash
python app.py
```

서버가 실행되면 브라우저에서 `http://127.0.0.1:5000` 또는 `http://localhost:5000`으로 접속할 수 있습니다.

## 프로젝트 구조

```
teambuilding_v10/
├── app.py                 # Flask 애플리케이션 진입점
├── config.py              # 설정 파일
├── database.py            # 데이터베이스 설정
├── requirements.txt       # Python 패키지 의존성
├── controllers/          # 라우트 컨트롤러
│   ├── user_controller.py
│   ├── friend_controller.py
│   ├── class_controller.py
│   ├── team_controller.py
│   ├── category_controller.py
│   ├── matching_controller.py
│   └── notification_controller.py
├── services/             # 비즈니스 로직
│   ├── user_service.py
│   ├── friend_service.py
│   ├── class_service.py
│   ├── team_service.py
│   ├── category_service.py
│   ├── matching_service.py
│   └── notification_service.py
├── models/               # 데이터베이스 모델
│   ├── user.py
│   ├── profile.py
│   ├── friend.py
│   ├── class_.py
│   ├── class_member.py
│   ├── category.py
│   ├── team.py
│   ├── team_member.py
│   ├── team_application.py
│   ├── team_invitation.py
│   ├── notification.py
│   └── matching_request.py
├── templates/            # Jinja2 템플릿
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── mypage.html
│   ├── friend_list.html
│   ├── class_list.html
│   ├── category_list.html
│   ├── team_list.html
│   ├── team_detail.html
│   └── notification_list.html
└── static/               # 정적 파일
    └── style.css
```

## 사용 방법

### 회원가입 및 로그인

1. 홈 페이지에서 "회원가입" 버튼 클릭
2. 아이디, 비밀번호, 이름, 학번, 학교 정보 입력
3. 성격, 목표, 기술 태그 입력 (선택사항)
4. 회원가입 완료 후 로그인

### 클래스 기반 팀 빌딩

1. 클래스 생성: 클래스 페이지에서 클래스 이름과 설명 입력하여 생성
2. 클래스 참여: 클래스 관리자가 공유한 참여 코드 입력
3. 팀 생성: 클래스를 선택한 후 팀 이름, 목표, 필요 기술, 정원 입력
4. 팀 지원: 클래스 내 모집 중인 팀에 지원 메시지와 함께 지원

### 카테고리 기반 팀 빌딩

1. 카테고리 생성: 카테고리 페이지에서 관심 주제 입력하여 생성
2. 팀 생성: 카테고리를 선택한 후 팀 정보 입력
3. 팀 지원: 카테고리 내 모집 중인 팀에 지원

### 친구 관리

1. 친구 검색: 친구 페이지에서 아이디로 사용자 검색
2. 친구 요청: 검색된 사용자에게 친구 요청 전송
3. 요청 수락: 받은 친구 요청 목록에서 수락/거절

### 알림 확인

상단 네비게이션의 알림 아이콘(🔔)을 클릭하여 알림 목록을 확인할 수 있습니다.

## 기술 스택

- Backend: Flask (Python)
- Database: SQLite (개발 환경)
- ORM: SQLAlchemy
- Frontend: HTML, CSS, Jinja2 템플릿

## 개발자

- 22121474 안동규
- 22313592 권강현
- 22310443 김민서
- 22312269 이보현
- 22110296 전형연


