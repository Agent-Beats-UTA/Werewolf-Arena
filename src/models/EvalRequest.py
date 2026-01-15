from typing import Any
from pydantic import BaseModel, HttpUrl

class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participant: HttpUrl
    role:str
    config: dict[str, Any]