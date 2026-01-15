from pydantic import BaseModel

class Suspect(BaseModel):
    suspect_agent_id:str
    suspect_reason:str