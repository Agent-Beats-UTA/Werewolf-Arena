from pydantic import BaseModel, HttpUrl, Field
from src.models.enum.Difficulty import Difficulty

class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participants: dict[str, HttpUrl]
    difficulty: Difficulty = Field(default=Difficulty.HARD, description="Game difficulty level: 'easy' or 'hard'")