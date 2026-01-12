from typing import TYPE_CHECKING

from src.models.abstract.Phase import Phase

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class RoundEnd(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)
        
    def run(self):
        pass
    