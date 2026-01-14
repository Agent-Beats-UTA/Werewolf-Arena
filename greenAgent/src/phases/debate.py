from typing import List, TYPE_CHECKING

from src.models.abstract.Phase import Phase
from src.models.Message import Message

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class Debate(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)

    async def run(self):
        game_state = self.game.state
        current_round = game_state.current_round
        speaking_order = game_state.speaking_order[current_round]
        participants = game_state.participants[current_round]
        # Create a dict for easy lookup by participant_id
        participants_dict = {p.id: p for p in participants}

        for _ in range(self.game.state.turns_to_speak_per_round):
            for participant_id in speaking_order:
                participant = participants_dict[participant_id]
                response = await self.messenger.talk_to_agent(
                    message=participant.get_debate_prompt(),
                    url=participant.url
                )

                # Parse response
                parsed = self._parse_json_response(response)
                response = parsed["message"]

                # Store response in chat history
                message = Message(
                    sender_id=participant_id,
                    content=message
                )
                if current_round not in game_state.chat_history:
                    game_state.chat_history[current_round] = []

                game_state.chat_history[current_round].append(message)