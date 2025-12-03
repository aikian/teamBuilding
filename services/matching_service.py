"""
Service layer for matching potential team members.

Provides a simple matching algorithm based on a user's profile
attributes (skills, personality, goals) compared against a team's
requirements. Returns a list of candidates sorted by a computed
score.
"""

from typing import List, Tuple

from models.user import User
from models.profile import Profile
from models.team import Team


class MatchingService:
    """Match users to teams based on shared attributes."""

    @staticmethod
    # 매칭 적합도 점수 계산
    def calculate_score(user: User, team: Team) -> int:
        """Simple score calculation: match skills count + personality + goal overlap."""
        user_profile: Profile = user.profile
        #프로필이 없다면 0점 처리
        if not user_profile:
            return 0
        score = 0
        # 1. Skills 매칭 계산
        if user_profile.skills and team.required_skills:
            user_skills = set(map(str.strip, user_profile.skills.split(',')))
            team_skills = set(map(str.strip, team.required_skills.split(',')))
            score += len(user_skills & team_skills) * 2
        # 2. 성격 매칭 계산
        if user_profile.personality and team.goal:
            if user_profile.personality.lower() in team.goal.lower():
                score += 1
        # 3. 목표 매칭 계산
        if user_profile.goals and team.goal:
            user_goals = set(map(str.strip, user_profile.goals.split(',')))
            goal_words = set(map(str.strip, team.goal.split()))
            score += len(user_goals & goal_words)
        return score

    @staticmethod
    def match_candidates(candidates: List[User], team: Team) -> List[Tuple[User, int]]:
        """Return candidates sorted by matching score (descending)."""
        scored = []
        for candidate in candidates:
            #각 후보자에 대해 점수 계산 후 리스트에 추가
            scored.append((candidate, MatchingService.calculate_score(candidate, team)))
        #내림차순으로 정렬
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored