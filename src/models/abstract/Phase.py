from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class Phase(ABC):

    def __init__(self, game: "Game", messenger: "Messenger"):
        self.game = game
        self.messenger = messenger

    @abstractmethod
    async def run(self):
        pass