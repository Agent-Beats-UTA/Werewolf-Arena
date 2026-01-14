from typing import List
from src.models.enum.Role import Role
from src.models.Suspect import Suspect
from src.game.GameData import GameData

from pydantic import BaseClass

class AgentState(BaseClass):
    suspects:List[Suspect] = []
    game_data:GameData
    
    def __init__(self, game_data:GameData):
        self.game_data = game_data
        
    def get_werewolf_kill_prompt(self):
        pass
    
    def get_seer_reveal_prompt(self):
        pass
    
    def get_bidding_prompt(self):
        pass
    
    def get_debate_prompt(self):
        pass
    
    def get_voting_prompt(self):
        pass
    
    def get_suspect_prompt(self):
        pass
    