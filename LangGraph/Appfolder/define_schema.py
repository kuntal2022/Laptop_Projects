from pydantic import BaseModel, Field

class ScoreClass(BaseModel):
    score: float = Field(..., description="Score between 0-10")
    feedback: str = Field(..., description="Detailed feedback max 100 words")

class TopicClass(BaseModel):
    topic: str = Field(..., description="UPSC essay topic")

from typing import TypedDict

class BaseStateClass(TypedDict):
    topic: str
    essay: str
    language_score: float
    language_feedback: str
    thought_score: float
    thought_feedback: str
    relevance_score: float
    relevance_feedback: str
    overall_score: float
    feed_back: str