from __future__ import annotations

import re
from collections.abc import Iterable

from .models import LeadCard, RedditPost


PAIN_MARKERS = {
    "looking for": 6,
    "need a": 5,
    "need an": 5,
    "any tool": 7,
    "is there a": 6,
    "how do i": 5,
    "manual": 7,
    "repetitive": 7,
    "takes too long": 8,
    "waste time": 7,
    "annoying": 5,
    "hate": 4,
    "can't find": 7,
    "struggling": 6,
    "pain": 5,
    "problem": 4,
}

BUYER_MARKERS = {
    "client": 7,
    "customer": 7,
    "pay": 6,
    "paid": 6,
    "budget": 8,
    "business": 5,
    "agency": 5,
    "shopify": 7,
    "ecommerce": 6,
    "saas": 5,
    "founder": 5,
    "team": 5,
}

URGENCY_MARKERS = {
    "today": 7,
    "this week": 6,
    "asap": 8,
    "urgent": 8,
    "launch": 6,
    "before": 4,
    "deadline": 7,
    "every day": 6,
    "daily": 5,
}

AUTOMATION_MARKERS = {
    "automate": 9,
    "workflow": 7,
    "spreadsheet": 7,
    "csv": 7,
    "scrape": 5,
    "report": 5,
    "email": 5,
    "crm": 7,
    "zapier": 8,
    "make.com": 8,
    "notion": 5,
    "airtable": 6,
    "api": 5,
    "dashboard": 5,
}


def score_posts(posts: Iterable[RedditPost]) -> list[LeadCard]:
    cards = [_score_post(post) for post in posts]
    return sorted(cards, key=lambda card: card.opportunity_score, reverse=True)


def _score_post(post: RedditPost) -> LeadCard:
    text = _normalize(post.full_text)
    pain_score, pain_signals = _score_markers(text, PAIN_MARKERS, 30)
    buyer_score, buyer_signals = _score_markers(text, BUYER_MARKERS, 25)
    urgency_score, urgency_signals = _score_markers(text, URGENCY_MARKERS, 20)
    automation_score, automation_signals = _score_markers(text, AUTOMATION_MARKERS, 20)
    engagement_score = min(5, round((post.score + post.num_comments * 2) / 25))
    validation_bonus = 0
    if pain_score >= 15 and automation_score >= 10:
        validation_bonus += 10
    if pain_score >= 10 and buyer_score >= 10:
        validation_bonus += 10

    total = min(100, pain_score + buyer_score + urgency_score + automation_score + engagement_score + validation_bonus)
    signals = tuple(dict.fromkeys([*pain_signals, *buyer_signals, *urgency_signals, *automation_signals]))
    opportunity = _opportunity_for(text, post)

    return LeadCard(
        post=post,
        opportunity_score=total,
        pain_score=pain_score,
        buyer_score=buyer_score,
        urgency_score=urgency_score,
        automation_score=automation_score,
        engagement_score=engagement_score,
        signals=signals[:10],
        target_user=opportunity["target_user"],
        pain_point=opportunity["pain_point"],
        mvp_idea=opportunity["mvp_idea"],
        github_project_name=opportunity["github_project_name"],
        first_build=opportunity["first_build"],
        monetization=opportunity["monetization"],
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _score_markers(text: str, markers: dict[str, int], cap: int) -> tuple[int, list[str]]:
    score = 0
    signals: list[str] = []
    for marker, weight in markers.items():
        if marker in text:
            score += weight
            signals.append(marker)
    return min(cap, score), signals


def _opportunity_for(text: str, post: RedditPost) -> dict[str, str]:
    if any(term in text for term in ["shopify", "ecommerce", "store", "product page", "dropship"]):
        return {
            "target_user": "Small ecommerce operators and Shopify store owners",
            "pain_point": "Store owners need faster ways to audit listings, pages, copy, and conversion gaps.",
            "mvp_idea": "A Shopify store roaster that turns a store URL into a practical conversion checklist.",
            "github_project_name": "shopify-store-roaster",
            "first_build": "Fetch one public store page, extract copy and metadata, then generate a Markdown audit.",
            "monetization": "Paid audits, template packs, or a small monthly monitoring plan.",
        }
    if any(term in text for term in ["spreadsheet", "csv", "excel", "airtable", "sheet"]):
        return {
            "target_user": "Operators who live in spreadsheets",
            "pain_point": "Teams spend too much time cleaning rows, summarizing changes, and explaining messy data.",
            "mvp_idea": "A CSV cleanup assistant that normalizes columns and writes an executive summary.",
            "github_project_name": "csv-ops-cleaner",
            "first_build": "Accept a CSV file, detect likely columns, flag issues, and output clean CSV plus notes.",
            "monetization": "One-off automation setup, hosted version, or paid templates for niche workflows.",
        }
    if any(term in text for term in ["email", "crm", "lead", "sales", "follow up", "customer"]):
        return {
            "target_user": "Small sales teams and solo founders",
            "pain_point": "Follow-up, lead triage, and CRM updates are repetitive but easy to miss.",
            "mvp_idea": "A lead follow-up drafter that turns notes into next actions and email drafts.",
            "github_project_name": "lead-followup-drafter",
            "first_build": "Paste lead notes, classify urgency, and generate next-step email drafts.",
            "monetization": "Setup service for small teams, niche CRM plugins, or paid workflow packs.",
        }
    if any(term in text for term in ["reddit", "subreddit", "post", "comments", "community"]):
        return {
            "target_user": "Indie hackers researching real demand",
            "pain_point": "It is hard to separate loud posts from useful pain points worth building for.",
            "mvp_idea": "A Reddit pain-point radar that ranks posts by urgency, buyer signals, and automation fit.",
            "github_project_name": "reddit-lead-radar",
            "first_build": "Scan a few subreddits for keywords and render the best leads into Markdown cards.",
            "monetization": "Research reports, private keyword monitors, or a hosted alerting dashboard.",
        }
    if any(term in text for term in ["meeting", "transcript", "call", "notes", "todo"]):
        return {
            "target_user": "Project managers and client-service teams",
            "pain_point": "Meeting notes often fail to become clear tasks, owners, and deadlines.",
            "mvp_idea": "A meeting-to-tasks converter that extracts decisions and next actions.",
            "github_project_name": "meeting-action-miner",
            "first_build": "Paste a transcript and output tasks grouped by owner and deadline.",
            "monetization": "Team setup, Notion/Jira integrations, or a lightweight paid web app.",
        }
    return {
        "target_user": f"People posting in r/{post.subreddit}",
        "pain_point": "The post hints at a repeated workflow or unmet tool need that may be worth validating.",
        "mvp_idea": "A tiny automation that accepts one clear input, performs one useful transformation, and returns one practical output.",
        "github_project_name": _slugify(post.title)[:48] or "tiny-workflow-helper",
        "first_build": "Interview one commenter, build a 24-hour prototype, and publish a small demo report.",
        "monetization": "Service-first delivery, then templates or a small hosted tool after validation.",
    }


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "tiny-workflow-helper"
