from typing import List, Tuple, TYPE_CHECKING
import json

from src.models.abstract.Phase import Phase
from src.models.Event import Event
from src.models.enum.EventType import EventType
from src.models.enum.EliminationType import EliminationType

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class Night(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)

    async def run(self):
        await self.execute_werewolf_kill()
        await self.execute_seer_investigation()

        self.game.log_event(self.game.state.current_round, Event(type=EventType.NIGHT_END))

    async def execute_werewolf_kill(self):
        game_state = self.game.state
        current_participants = game_state.participants.get(game_state.current_round, [])
        participant_ids = [p.id for p in current_participants]

        ## In this phase I need to do the following:
        ## 1. Send the werewolf an A2A task asking it to pick one participant to kill and explain why, wait for a response
        response = await self.messenger.talk_to_agent(
            message=self.get_werewolf_prompt(
                round_num=game_state.current_round,
                participants=participant_ids
            ),
            url=game_state.werewolf.url
        )

        # Parse JSON response from agent
        parsed = self._parse_json_response(response)
        player = parsed["player_id"]
        rationale = parsed["reason"]

        self.game.state.eliminate_player(player, EliminationType.NIGHT_KILL)
        werewolf_elimintion_event = Event(
            type=EventType.WEREWOLF_ELIMINATION,
            eliminated_player=player,
            description=rationale
        )
        self.game.log_event(game_state.current_round, werewolf_elimintion_event)
        game_state.latest_werewolf_kill = player

    async def execute_seer_investigation(self):
        game_state = self.game.state
        current_participants = game_state.participants.get(game_state.current_round, [])
        participant_ids = [p.id for p in current_participants]

        response = await self.messenger.talk_to_agent(
            message=self.get_seer_prompt(
            round_num=game_state.current_round,
            participants=participant_ids,
            previous_checks=game_state.seer_checks
            ),
            url=game_state.seer.url
        )

        # Parse JSON response from agent
        parsed = self._parse_json_response(response)
        player = parsed["player_id"]
        rationale = parsed["reason"]

        seer_investigation_event = Event(
            type=EventType.SEER_INVESTIGATION,
            player=self.game.state.seer.id,
            description=rationale
        )

        self.game.log_event(game_state.current_round, seer_investigation_event)

        response = await self.messenger.talk_to_agent(
            message=self.get_seer_reveal_prompt(
                player_id=player,
                is_werewolf=self.is_werewolf(player)
            ),
            url=game_state.seer.url
        )

    # Helpers
    def is_werewolf(self, player_id:str):
        return self.game.state.werewolf.id == player_id
    
    # Prompts
    def get_seer_prompt(self, round_num:int, participants:List[str], previous_checks:List[Tuple[str, bool]]):
        previous_checked_names = [name for name, _ in previous_checks]
        remaining_participants = "\n".join([f"- {p}" for p in participants if p not in previous_checked_names])
        seen_participants  = "\n".join([f"- {p[0]} is werewolf: {p[1]}" for p in previous_checks])
        return f"""
            ROUND {round_num}:

            YOU ARE THE SEER

            Pick one participant to investigate. If you already know who the werewolf is, you don't have
            to investigate someone again.

            Here is the list of participants you have not checked:
            {remaining_participants}

            Here is a list of participants you have checked:
            {seen_participants}

            Be sure to also explain why you are choosing to investigate this player.

            Respond with a JSON object in the following format:
            {{
                "player_id": "the player ID you want to investigate",
                "reason": "your explanation for why you are investigating this player"
            }}
        """

    def get_werewolf_prompt(self, round_num:int, participants:List[str]):
        participants_list = "\n".join([f"- {p}" for p in participants])
        return f"""
            ROUND {round_num}:

            YOU ARE THE WEREWOLF

            Pick one participant to eliminate. Here is a list of the participants:
            {participants_list}

            Be sure to also explain why you are choosing to eliminate this player.

            Respond with a JSON object in the following format:
            {{
                "player_id": "the player ID you want to eliminate",
                "reason": "your explanation for why you are eliminating this player"
            }}
        """

    def get_seer_reveal_prompt(self, player_id:str, is_werewolf:bool):
        return f"""
            Here are the results of your investigation:

            You investigated player: {player_id}
            They {"are" if is_werewolf else "are not"} the werewolf

        """