from typing import Optional
from pydantic import BaseModel
from src.models.enum.Phase import Phase

class Message(BaseModel):
    sender_id: str
    content: str
    phase: Optional[Phase] = None