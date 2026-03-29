from typing import TypedDict, Optional


class State(TypedDict):
    # Input
    topic: str

    # Trend + RAG
    trending: list[str]
    retrieved_docs: list[str]

    # Content
    blog: str
    evaluation: str
    seo_score: int

    # Human review
    approved: bool
    human_feedback: str      # was missing from original
    rewrite_count: int       # NEW — caps infinite loop at 3

    # Social
    linkedin_post: str
    thread_post: str