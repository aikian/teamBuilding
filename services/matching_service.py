"""
사용자의 프로필 속성(기술, 성격, 목표)을 팀 요구사항과 비교하여
간단한 매칭 점수를 계산하고, 후보자를 점수 내림차순으로 반환하는 서비스입니다.
필요시 클래스나 카테고리 기반 후보자 필터링도 지원합니다.

"""

from typing import List, Tuple

from models.user import User
from models.profile import Profile
from models.team import Team


class MatchingService:
    """Match users to teams based on shared attributes."""

    @staticmethod
    def calculate_score(user: User, team: Team) -> int:
        """Simple score calculation: match skills count + personality + goal overlap."""
        user_profile: Profile = user.profile
        if not user_profile:
            return 0

        score = 0

        # 1. Skills 매칭 계산 (쉼표 구분, 공백 제거, 소문자 통일)
        if user_profile.skills and team.required_skills:
            user_skills = set(x.strip().lower() for x in user_profile.skills.split(','))
            team_skills = set(x.strip().lower() for x in team.required_skills.split(','))
            score += len(user_skills & team_skills) * 2

        # 2. 성격 매칭 계산 (소문자 통일)
        if user_profile.personality and team.goal:
            if user_profile.personality.strip().lower() in team.goal.lower():
                score += 1

        # 3. 목표 매칭 계산 (쉼표 구분, 공백 제거, 소문자 통일)
        if user_profile.goals and team.goal:
            user_goals = set(x.strip().lower() for x in user_profile.goals.split(','))
            goal_words = set(x.strip().lower() for x in team.goal.split())
            score += len(user_goals & goal_words)

        return score


    @staticmethod
    def match_candidates(
        candidates: list[User], 
        team: Team, 
        filter_class: bool = False, 
        filter_category: bool = False
    ) -> list[tuple[User, int]]:
        """Return candidates sorted by matching score (descending)."""
    
        scored = []

        # 1. 후보자 필터링
        if filter_class and team.class_id:  # 팀이 클래스에 속해 있다면
            candidates = [
                c for c in candidates 
                if getattr(c, 'class_id', None) == team.class_id
            ]

        if filter_category and team.category_id:  # 팀이 카테고리에 속해 있다면
            candidates = [
                c for c in candidates 
                if getattr(c, 'category_id', None) == team.category_id
            ]

        # 2. 점수 계산
        for candidate in candidates:
            score = MatchingService.calculate_score(candidate, team)
            scored.append((candidate, score))

        # 3. 내림차순 정렬
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
