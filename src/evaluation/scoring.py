from pydantic import BaseModel
from src.game.GameData import GameData
from src.models.enum.Role import Role
from src.models.enum.EventType import EventType

class Scoring(BaseModel):
    game_state: GameData
    
    def score_werewolf(self):
        # Werewolf scores points the longer it lasts into the game
        # The werewolf also scores points for each agent it's able to convince it's not the werewolf
        # Scores bonus points of wins round
        if not self.game_state.werewolf:
            return 0
        
        score = 0
        werewolf_id = self.game_state.werewolf.id
        
        score += self.game_state.current_round * 10
        
        for round_num, votes in self.game_state.votes.items():
            for vote in votes:
                if vote.voted_for_id != werewolf_id:
                    score += 5
        
        if self.game_state.winner == "werewolf":
            score += 50
        
        return score
    
    def score_seer(self):
        # scores points for shorter rounds
        # looses increasing number of points each round after werewolf is succcessfully revealed to simulate inaction after the werewolf is revealed
        if not self.game_state.seer:
            return 0
        
        score = 0
        werewolf_revealed_round = None
        
        for round_num, events in self.game_state.events.items():
            for event in events:
                if event.type == EventType.SEER_INVESTIGATION:
                    if werewolf_revealed_round is None:
                        werewolf_revealed_round = round_num
        
        if werewolf_revealed_round:
            score += (10 - werewolf_revealed_round) * 5
            
            for round_num in range(werewolf_revealed_round + 1, self.game_state.current_round + 1):
                penalty = (round_num - werewolf_revealed_round) * 3
                score -= penalty
        else:
            score += (10 - self.game_state.current_round) * 5
        
        return max(0, score)
    
    def score_villager(self):
        # Scores points for correctly suspecting the werewolf
        # Bonus points for shorter rounds
        if not self.game_state.werewolf:
            return 0

        score = 0
        werewolf_id = self.game_state.werewolf.id

        for round_num, votes in self.game_state.votes.items():
            for vote in votes:
                if vote.voted_for_id == werewolf_id:
                    score += 10

        score += (10 - self.game_state.current_round) * 3

        if self.game_state.winner == "villagers":
            score += 30

        return score

    def score_doctor(self):
        # Doctor scores points for successful saves (saving the werewolf's target)
        # Bonus points for each round the doctor survives
        # Bonus points if villagers win
        if not self.game_state.doctor:
            return 0

        score = 0

        # Points for successful saves - check if saved player was targeted by werewolf
        doctor_saves = self.game_state.doctor_saves or {}
        for round_num, saved_player in doctor_saves.items():
            round_events = self.game_state.events.get(round_num, [])
            for event in round_events:
                if event.type == EventType.WEREWOLF_ELIMINATION_FAILURE:
                    if getattr(event, "player", None) == saved_player:
                        score += 25  # Major points for successful save
                        break

        # Survival bonus - points for each round survived
        score += self.game_state.current_round * 5

        # Win bonus
        if self.game_state.winner == "villagers":
            score += 30

        return score