from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

from .models import RedditPost


DEFAULT_USER_AGENT = "reddit-lead-radar/0.1 (+https://github.com/) research tool"


class RedditClient:
    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, delay_seconds: float = 2.0) -> None:
        self.user_agent = user_agent
        self.delay_seconds = max(0.0, delay_seconds)
        self.errors: list[str] = []

    def search(
        self,
        subreddits: Iterable[str],
        keywords: Iterable[str],
        limit: int = 15,
        days: int = 30,
        comments: int = 0,
    ) -> list[RedditPost]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        seen: set[str] = set()
        posts: list[RedditPost] = []

        for subreddit in subreddits:
            clean_subreddit = subreddit.strip().lstrip("r/")
            if not clean_subreddit:
                continue
            for keyword in keywords:
                clean_keyword = keyword.strip()
                if not clean_keyword:
                    continue
                try:
                    found_posts = self._search_subreddit(clean_subreddit, clean_keyword, limit)
                except RuntimeError as exc:
                    self.errors.append(f"r/{clean_subreddit} '{clean_keyword}': {exc}")
                    self._pause()
                    continue
                for post in found_posts:
                    if post.id in seen or post.created_at < cutoff:
                        continue
                    seen.add(post.id)
                    if comments > 0:
                        post = self.with_comments(post, limit=comments)
                    posts.append(post)
                    self._pause()

        return posts

    def _search_subreddit(self, subreddit: str, keyword: str, limit: int) -> list[RedditPost]:
        params = urllib.parse.urlencode(
            {
                "q": keyword,
                "restrict_sr": "on",
                "sort": "new",
                "t": "month",
                "limit": str(limit),
                "raw_json": "1",
            }
        )
        url = f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/search.json?{params}"
        payload = self._get_json(url)
        children = payload.get("data", {}).get("children", [])
        return [self._parse_post(child.get("data", {})) for child in children if child.get("data")]

    def with_comments(self, post: RedditPost, limit: int = 3) -> RedditPost:
        url = f"https://www.reddit.com{post.permalink}.json?limit={limit}&raw_json=1"
        try:
            payload = self._get_json(url)
        except RuntimeError:
            return post
        comments = tuple(_extract_comments(payload, limit=limit))
        return RedditPost(**{**post.__dict__, "comments": comments})

    def _get_json(self, url: str) -> dict[str, Any] | list[Any]:
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"could not read {url}") from exc

    def _parse_post(self, data: dict[str, Any]) -> RedditPost:
        permalink = str(data.get("permalink") or "")
        return RedditPost(
            id=str(data.get("id") or ""),
            subreddit=str(data.get("subreddit") or ""),
            title=str(data.get("title") or "").strip(),
            selftext=str(data.get("selftext") or "").strip(),
            author=str(data.get("author") or "[unknown]"),
            permalink=permalink,
            url=f"https://www.reddit.com{permalink}" if permalink else str(data.get("url") or ""),
            score=int(data.get("score") or 0),
            num_comments=int(data.get("num_comments") or 0),
            created_utc=float(data.get("created_utc") or 0),
        )

    def _pause(self) -> None:
        if self.delay_seconds:
            time.sleep(self.delay_seconds)


def _extract_comments(payload: dict[str, Any] | list[Any], limit: int) -> list[str]:
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    listing = payload[1].get("data", {}).get("children", [])
    comments: list[str] = []
    for child in listing:
        if len(comments) >= limit:
            break
        data = child.get("data", {})
        body = str(data.get("body") or "").strip()
        if body and body not in {"[deleted]", "[removed]"}:
            comments.append(body)
    return comments
