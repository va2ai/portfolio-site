"""Reddit search and content retrieval via PRAW."""
from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..base import BaseTool, ToolOutput


class RedditSearchInput(BaseModel):
    query: str
    subreddit: str = ""  # empty = search all of Reddit
    sort: str = "relevance"  # relevance | hot | top | new | comments
    time_filter: str = "all"  # all | day | week | month | year
    limit: int = 10


class RedditSearchTool(BaseTool):
    name = "reddit_search"
    description = "Search Reddit posts and comments. Find discussions, opinions, experiences, and community knowledge on any topic."
    safety_level = "safe"
    timeout_seconds = 30

    def input_schema(self) -> type[BaseModel]:
        return RedditSearchInput

    async def execute(self, input_data: BaseModel) -> ToolOutput:
        try:
            reddit = _get_reddit()
            if not reddit:
                return ToolOutput(success=False, error="Reddit credentials not configured. Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET in .env")

            if input_data.subreddit:
                sub = reddit.subreddit(input_data.subreddit)
                results = sub.search(input_data.query, sort=input_data.sort, time_filter=input_data.time_filter, limit=input_data.limit)
            else:
                results = reddit.subreddit("all").search(input_data.query, sort=input_data.sort, time_filter=input_data.time_filter, limit=input_data.limit)

            posts = []
            for post in results:
                posts.append({
                    "title": post.title,
                    "subreddit": str(post.subreddit),
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "selftext": (post.selftext[:500] + "...") if len(post.selftext) > 500 else post.selftext,
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else "[deleted]",
                })

            return ToolOutput(success=True, result={"posts": posts, "count": len(posts)})
        except Exception as e:
            return ToolOutput(success=False, error=str(e))


class RedditPostInput(BaseModel):
    url: str  # reddit post URL or post ID
    comment_limit: int = 10
    comment_sort: str = "best"  # best | top | new | controversial


class RedditReadPostTool(BaseTool):
    name = "reddit_read_post"
    description = "Read a Reddit post and its top comments. Get the full discussion thread with comment scores and replies."
    safety_level = "safe"
    timeout_seconds = 30

    def input_schema(self) -> type[BaseModel]:
        return RedditPostInput

    async def execute(self, input_data: BaseModel) -> ToolOutput:
        try:
            reddit = _get_reddit()
            if not reddit:
                return ToolOutput(success=False, error="Reddit credentials not configured")

            submission = reddit.submission(url=input_data.url)
            submission.comment_sort = input_data.comment_sort
            submission.comments.replace_more(limit=0)

            comments = []
            for c in submission.comments[:input_data.comment_limit]:
                comments.append({
                    "author": str(c.author) if c.author else "[deleted]",
                    "body": (c.body[:400] + "...") if len(c.body) > 400 else c.body,
                    "score": c.score,
                })

            return ToolOutput(success=True, result={
                "title": submission.title,
                "subreddit": str(submission.subreddit),
                "selftext": submission.selftext,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "url": f"https://reddit.com{submission.permalink}",
                "author": str(submission.author) if submission.author else "[deleted]",
                "comments": comments,
            })
        except Exception as e:
            return ToolOutput(success=False, error=str(e))


class RedditSubredditInput(BaseModel):
    subreddit: str
    sort: str = "hot"  # hot | new | top | rising
    time_filter: str = "day"  # day | week | month | year | all (for top only)
    limit: int = 10


class RedditSubredditTool(BaseTool):
    name = "reddit_subreddit"
    description = "Browse a subreddit's posts by hot, new, top, or rising. Get a snapshot of what a community is discussing."
    safety_level = "safe"
    timeout_seconds = 30

    def input_schema(self) -> type[BaseModel]:
        return RedditSubredditInput

    async def execute(self, input_data: BaseModel) -> ToolOutput:
        try:
            reddit = _get_reddit()
            if not reddit:
                return ToolOutput(success=False, error="Reddit credentials not configured")

            sub = reddit.subreddit(input_data.subreddit)

            if input_data.sort == "hot":
                posts_iter = sub.hot(limit=input_data.limit)
            elif input_data.sort == "new":
                posts_iter = sub.new(limit=input_data.limit)
            elif input_data.sort == "top":
                posts_iter = sub.top(time_filter=input_data.time_filter, limit=input_data.limit)
            elif input_data.sort == "rising":
                posts_iter = sub.rising(limit=input_data.limit)
            else:
                posts_iter = sub.hot(limit=input_data.limit)

            posts = []
            for post in posts_iter:
                posts.append({
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "selftext": (post.selftext[:300] + "...") if len(post.selftext) > 300 else post.selftext,
                    "author": str(post.author) if post.author else "[deleted]",
                })

            return ToolOutput(success=True, result={
                "subreddit": input_data.subreddit,
                "sort": input_data.sort,
                "posts": posts,
                "count": len(posts),
            })
        except Exception as e:
            return ToolOutput(success=False, error=str(e))


def _get_reddit():
    """Initialize PRAW Reddit instance from env vars."""
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "ai-agent-platform:v1.0 (by /u/ai_agent)")

    if not client_id or not client_secret:
        return None

    import praw
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
