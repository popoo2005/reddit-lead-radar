from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import score_posts
from .models import RedditPost
from .reddit import RedditClient
from .report import write_json, write_markdown


DEFAULT_SUBREDDITS = ["SideProject", "SaaS", "nocode", "automation", "Entrepreneur"]
DEFAULT_KEYWORDS = [
    "looking for tool",
    "need a tool",
    "manual workflow",
    "automate",
    "shopify automation",
    "spreadsheet problem",
    "customer support automation",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="reddit-lead-radar",
        description="Find public Reddit pain-point posts worth validating as tiny automation projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan public Reddit JSON endpoints.")
    scan.add_argument("--subreddits", default=",".join(DEFAULT_SUBREDDITS), help="Comma-separated subreddit names.")
    scan.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS), help="Comma-separated search phrases.")
    scan.add_argument("--limit", type=int, default=10, help="Posts to request per subreddit/keyword pair.")
    scan.add_argument("--days", type=int, default=30, help="Ignore posts older than this many days.")
    scan.add_argument("--comments", type=int, default=0, help="Fetch this many top comments per post.")
    scan.add_argument("--delay", type=float, default=2.0, help="Delay between Reddit requests in seconds.")
    scan.add_argument("--out", default="reports/latest.md", help="Markdown report path.")
    scan.add_argument("--json-out", default="reports/latest.json", help="JSON report path.")

    analyze = subparsers.add_parser("analyze", help="Analyze a local JSON file of Reddit-like posts.")
    analyze.add_argument("input", help="Path to a JSON file with a list of posts.")
    analyze.add_argument("--out", default="reports/local.md", help="Markdown report path.")
    analyze.add_argument("--json-out", default="reports/local.json", help="JSON report path.")

    args = parser.parse_args(argv)

    if args.command == "scan":
        subreddits = _split_csv(args.subreddits)
        keywords = _split_csv(args.keywords)
        client = RedditClient(delay_seconds=args.delay)
        posts = client.search(subreddits, keywords, limit=args.limit, days=args.days, comments=args.comments)
        cards = score_posts(posts)
        query_summary = f"subreddits={subreddits}; keywords={keywords}; days={args.days}"
        _write_outputs(cards, query_summary, Path(args.out), Path(args.json_out))
        for error in client.errors:
            print(f"Warning: {error}")
        print(f"Wrote {len(cards)} leads to {args.out} and {args.json_out}")
        return 0

    if args.command == "analyze":
        posts = _load_posts(Path(args.input))
        cards = score_posts(posts)
        query_summary = f"local_file={args.input}"
        _write_outputs(cards, query_summary, Path(args.out), Path(args.json_out))
        print(f"Wrote {len(cards)} leads to {args.out} and {args.json_out}")
        return 0

    parser.error("Unknown command")
    return 2


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _write_outputs(cards, query_summary: str, markdown_path: Path, json_path: Path) -> None:
    write_markdown(markdown_path, cards, query_summary)
    write_json(json_path, cards)


def _load_posts(path: Path) -> list[RedditPost]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    posts: list[RedditPost] = []
    for item in raw:
        posts.append(
            RedditPost(
                id=str(item.get("id", "")),
                subreddit=str(item.get("subreddit", "")),
                title=str(item.get("title", "")),
                selftext=str(item.get("selftext", "")),
                author=str(item.get("author", "")),
                permalink=str(item.get("permalink", "")),
                url=str(item.get("url", "")),
                score=int(item.get("score", 0)),
                num_comments=int(item.get("num_comments", 0)),
                created_utc=float(item.get("created_utc", 0)),
                comments=tuple(item.get("comments", [])),
            )
        )
    return posts


if __name__ == "__main__":
    raise SystemExit(main())
