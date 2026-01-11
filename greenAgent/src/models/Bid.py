from pydantic import BaseModel

class Bid(BaseModel):
    participant_id: str
    amount: int