import unittest

from reddit_lead_radar.analysis import score_posts
from reddit_lead_radar.models import RedditPost
from reddit_lead_radar.report import render_markdown


class ReportTest(unittest.TestCase):
    def test_report_contains_thread_and_project_name(self) -> None:
        post = RedditPost(
            id="abc",
            subreddit="automation",
            title="Need a tool for CSV cleanup",
            selftext="Our spreadsheet workflow is manual and annoying.",
            author="ops",
            permalink="/r/automation/comments/abc/example/",
            url="https://reddit.com/r/automation/comments/abc/example/",
            score=10,
            num_comments=3,
            created_utc=1_800_000_000,
        )
        report = render_markdown(score_posts([post]), "test query")

        self.assertIn("Reddit Lead Radar Report", report)
        self.assertIn("csv-ops-cleaner", report)
        self.assertIn("https://reddit.com/r/automation/comments/abc/example/", report)


if __name__ == "__main__":
    unittest.main()
