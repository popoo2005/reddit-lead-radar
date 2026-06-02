from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class RedditPost:
    id: str
    subreddit: str
    title: str
    selftext: str
    author: str
    permalink: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    comments: tuple[str, ...] = field(default_factory=tuple)

    @property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc, tz=timezone.utc)

    @property
    def full_text(self) -> str:
        return "\n".join(part for part in [self.title, self.selftext, *self.comments] if part)


@dataclass(frozen=True)
class LeadCard:
    post: RedditPost
    opportunity_score: int
    pain_score: int
    buyer_score: int
    urgency_score: int
    automation_score: int
    engagement_score: int
    signals: tuple[str, ...]
    target_user: str
    pain_point: str
    mvp_idea: str
    github_project_name: str
    first_build: str
    monetization: str

