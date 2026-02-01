from pydantic import BaseModel, HttpUrl, Field
from src.models.EvalConfig import EvalConfig

class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participants: dict[str, HttpUrl]
    config: EvalConfig = Field(default_factory=EvalConfig, description="Evaluation configuration")