from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import LeadCard


def render_markdown(cards: list[LeadCard], query_summary: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Reddit Lead Radar Report",
        "",
        f"Generated: {now}",
        f"Query: {query_summary}",
        f"Leads found: {len(cards)}",
        "",
        "This report ranks public Reddit posts by pain signals, buyer intent, urgency, automation fit, and engagement.",
        "",
    ]

    for index, card in enumerate(cards, start=1):
        post = card.post
        lines.extend(
            [
                f"## {index}. {post.title}",
                "",
                f"Score: **{card.opportunity_score}/100**",
                f"Subreddit: r/{post.subreddit}",
                f"Author: u/{post.author}",
                f"Posted: {post.created_at.strftime('%Y-%m-%d')}",
                f"Thread: {post.url}",
                "",
                "| Dimension | Score |",
                "| --- | ---: |",
                f"| Pain | {card.pain_score} |",
                f"| Buyer signal | {card.buyer_score} |",
                f"| Urgency | {card.urgency_score} |",
                f"| Automation fit | {card.automation_score} |",
                f"| Engagement | {card.engagement_score} |",
                "",
                f"Signals: {', '.join(card.signals) if card.signals else 'No explicit markers, review manually.'}",
                "",
                "### Opportunity Card",
                "",
                f"- Target user: {card.target_user}",
                f"- Pain point: {card.pain_point}",
                f"- MVP idea: {card.mvp_idea}",
                f"- GitHub project name: `{card.github_project_name}`",
                f"- First build: {card.first_build}",
                f"- Monetization: {card.monetization}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def write_markdown(path: Path, cards: list[LeadCard], query_summary: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(cards, query_summary), encoding="utf-8")


def write_json(path: Path, cards: list[LeadCard]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "score": card.opportunity_score,
            "signals": list(card.signals),
            "post": {
                "id": card.post.id,
                "subreddit": card.post.subreddit,
                "title": card.post.title,
                "author": card.post.author,
                "url": card.post.url,
                "created_utc": card.post.created_utc,
                "score": card.post.score,
                "num_comments": card.post.num_comments,
            },
            "opportunity": {
                "target_user": card.target_user,
                "pain_point": card.pain_point,
                "mvp_idea": card.mvp_idea,
                "github_project_name": card.github_project_name,
                "first_build": card.first_build,
                "monetization": card.monetization,
            },
        }
        for card in cards
    ]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

