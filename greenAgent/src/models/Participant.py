from pydantic import BaseModel
from src.models.enum.Role import Role
from src.models.enum.Status import Status

class Participant(BaseModel):
    id:str
    url:str
    role: Role
    status: Status