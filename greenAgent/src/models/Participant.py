from pydantic import BaseModel
from src.models.enum.Role import Role

class Participant(BaseModel):
    id:str
    url:str
    role: Role