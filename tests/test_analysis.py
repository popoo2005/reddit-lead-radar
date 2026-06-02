import unittest

from reddit_lead_radar.analysis import score_posts
from reddit_lead_radar.models import RedditPost


class AnalysisTest(unittest.TestCase):
    def test_shopify_post_gets_high_relevant_opportunity(self) -> None:
        post = RedditPost(
            id="abc",
            subreddit="SideProject",
            title="Looking for a tool to automate Shopify product page audits",
            selftext="I have a client and this manual workflow takes too long every day.",
            author="founder",
            permalink="/r/SideProject/comments/abc/example/",
            url="https://reddit.com/r/SideProject/comments/abc/example/",
            score=22,
            num_comments=9,
            created_utc=1_800_000_000,
        )

        card = score_posts([post])[0]

        self.assertGreaterEqual(card.opportunity_score, 70)
        self.assertEqual(card.github_project_name, "shopify-store-roaster")
        self.assertIn("shopify", card.mvp_idea.lower())

    def test_generic_post_still_produces_mvp_card(self) -> None:
        post = RedditPost(
            id="def",
            subreddit="SaaS",
            title="I built a tiny dashboard",
            selftext="Curious what people think.",
            author="maker",
            permalink="/r/SaaS/comments/def/example/",
            url="https://reddit.com/r/SaaS/comments/def/example/",
            score=1,
            num_comments=0,
            created_utc=1_800_000_000,
        )

        card = score_posts([post])[0]

        self.assertGreaterEqual(card.opportunity_score, 0)
        self.assertTrue(card.first_build)


if __name__ == "__main__":
    unittest.main()
