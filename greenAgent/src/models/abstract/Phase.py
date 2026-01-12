from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import json

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

    def _parse_json_response(self, response: str) -> dict:
        """
        Parse JSON response from agent.
        Expected format varies by phase, but generally: {"key": "value", ...}
        """
        try:
            # Try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from markdown code blocks
            # Sometimes LLMs wrap JSON in ```json ... ```
            json_match = response.find("```json")
            if json_match != -1:
                start = response.find("\n", json_match) + 1
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)

            # Try without the json marker
            json_match = response.find("```")
            if json_match != -1:
                start = response.find("\n", json_match) + 1
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)

            # If all else fails, raise an error with the response
            raise ValueError(f"Could not parse JSON from agent response: {response}")