from typing import TYPE_CHECKING, Dict, Any

from src.models.abstract.Phase import Phase
from src.game.analytics import compute_game_analytics, render_summary_text
from src.evaluation.scoring import Scoring
from src.models.enum.Role import Role

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class GameEnd(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)
        self.analytics: Dict[str, Any] = {}
        
    async def run(self) -> Dict[str, Any]:
        analytics = compute_game_analytics(self.game.state)
        scores = self.compute_scores()
        analytics["scores"] = scores
        analytics["summary_text"] = render_summary_text(analytics)
        return analytics
    
    def compute_scores(self) -> Dict[str, int]:
        scoring = Scoring(game_state=self.game.state)
        scores = {}

        # Score both werewolves
        if self.game.state.primary_werewolf:
            scores[self.game.state.primary_werewolf.id] = scoring.score_werewolf(
                self.game.state.primary_werewolf.id
            )
        if self.game.state.secondary_werewolf:
            scores[self.game.state.secondary_werewolf.id] = scoring.score_werewolf(
                self.game.state.secondary_werewolf.id
            )

        if self.game.state.seer:
            scores[self.game.state.seer.id] = scoring.score_seer()

        if self.game.state.doctor:
            scores[self.game.state.doctor.id] = scoring.score_doctor()

        for villager in self.game.state.villagers:
            scores[villager.id] = scoring.score_villager()

        return scores