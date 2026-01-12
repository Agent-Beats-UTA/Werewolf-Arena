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
        chat_history = game_state.chat_history.get(current_round, [])
        night_elimination_message = self.game.get_night_elimination_message(current_round)
        participants = game_state.participants[current_round]
        # Create a dict for easy lookup by participant_id
        participants_dict = {p.id: p for p in participants}

        for _ in range(self.game.state.turns_to_speak_per_round):
            for participant_id in speaking_order:
                participant = participants_dict[participant_id]
                response = await self.messenger.talk_to_agent(
                    message=self.get_debate_prompt(
                        user_role=participant.role,
                        chat_history=chat_history,
                        speaking_order=speaking_order,
                        night_elimination_message=night_elimination_message
                    ),
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


    # Prompts
    def get_debate_prompt(self, user_role:str, chat_history:List[Message], speaking_order:List[str], night_elimination_message:str):
        prompt = f"""
        You are participating in the Debate phase of a Werewolf game as a {user_role}.
        
        The debate phase allows players to discuss and strategize before voting.
        
        Here is the chat history so far:
        {"\n".join([f"{msg.sender_id}: {msg.content}" for msg in chat_history])}
        
        The established speaking order for this round is:
        {', '.join(speaking_order)}
        
        Additionally, here is what happened during the night:
        {night_elimination_message}
        
        Please contribute to the discussion in accordance with your role and the ongoing strategies.

        Please respond in json format:
        {{
            "message": "<your message here>"
        }}
        """
        return prompt
    