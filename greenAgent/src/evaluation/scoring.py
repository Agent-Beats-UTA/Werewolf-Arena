from pydantic import BaseModel
from src.game.GameData import GameData

class Scoring(BaseModel):
    def __init__(self, gameState:GameData):
        super().__init__(gameState)
    
    def score_werewolf(self):
        # Werewolf scores points the longer it lasts into the game
        # The werewolf also scores points for each agent it's able to convince it's not the werewolf
        # Scores bonus points of wins round
        pass
    
    def score_seer(self):
        # scores points for shorter rounds
        # looses increasing number of points each round after werewolf is succcessfully revealed to simulate inaction after the werewolf is revealed
        pass
    
    def score_villager(self):
        # Scores points for correctly suspecting the werewolf
        # Bonus points for shorter rounds
        pass