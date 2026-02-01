from pydantic import BaseModel, Field
from src.models.enum.Difficulty import Difficulty


class EvalConfig(BaseModel):
    """Configuration options for the evaluation, passed via the [config] section."""
    difficulty: Difficulty = Field(default=Difficulty.HARD, description="Game difficulty level: 'easy' or 'hard'")
