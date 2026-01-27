from typing import TYPE_CHECKING

from src.models.abstract.Phase import Phase
from src.models.Event import Event
from src.models.enum.EventType import EventType
from src.models.enum.EliminationType import EliminationType
from src.models.enum.EliminationType import EliminationStatus

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class Night(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)

    async def run(self):
        await self.game.log(f"[Night] Round {self.game.state.current_round}")
        await self.execute_doctor_save()
        await self.execute_werewolf_kill()
        await self.execute_seer_investigation()

        self.game.log_event(self.game.state.current_round, Event(type=EventType.NIGHT_END))
        
    async def execute_doctor_save(self):
        game_state = self.game.state
        doctor = self.game.state.doctor

        if game_state.doctor is None:
            await self.game.log(f"[Night] doctor is dead, skipping save")
            return

        await self.game.log(f"[Night] Doctor choosing target to save...")

        # Try up to 3 times if doctor tries to save themselves
        max_attempts = 3
        for attempt in range(max_attempts):
            response = await doctor.talk_to_agent(
                prompt=doctor.get_doctor_prompt()
            )

            player = response["player_id"]
            rationale = response["reason"]

            # Validate doctor is not saving themselves
            if player == doctor.id:
                await self.game.log(f"[Night] Doctor tried to save themselves (attempt {attempt + 1}/{max_attempts}), re-prompting...")
                if attempt == max_attempts - 1:
                    await self.game.log(f"[Night] Doctor failed to choose valid target after {max_attempts} attempts, no save this round")
                    return
                continue

            break

        doctor_save_event = Event(
            type=EventType.DOCTOR_SAVE,
            player=player,
            description=rationale
        )

        self.game.log_event(game_state.current_round, doctor_save_event)

        game_state.doctor_saves[game_state.current_round] = player

    async def execute_werewolf_kill(self):
        game_state = self.game.state

        # Check if primary werewolf is still alive (secondary would have been promoted)
        if game_state.primary_werewolf is None:
            await self.game.log("[Night] All werewolves are dead, skipping kill")
            return

        await self.game.log(f"[Night] Werewolf {game_state.primary_werewolf.id[:8]} choosing victim...")
        response = await game_state.primary_werewolf.talk_to_agent(
            prompt=game_state.primary_werewolf.get_werewolf_prompt(),
        )

        player = response["player_id"]
        rationale = response["reason"]
        await self.game.log(f"[Night] Werewolf tried to eliminate {player[:8]}: {rationale[:50]}...")

        ## Check for doctor save
        doc_save_player_id = game_state.doctor_saves.get(game_state.current_round)

        if doc_save_player_id is not None and player == doc_save_player_id:
            ## Elimination failed
            await self.game.log(f"[Night] Werewolf tried to eliminate {player} but failed because {player} was saved by the doctor")
            werewolf_elimination_event_failure = Event(
                type=EventType.WEREWOLF_ELIMINATION_FAILURE,
                player=player,
                description=f"Werewolf tried to eliminate {player} but failed because {player} was saved by the doctor"
            )
            self.game.log_event(game_state.current_round, werewolf_elimination_event_failure)
            
            game_state.latest_werewolf_kill = (player, EliminationStatus.FAIL)
        else:
            self.game.state.eliminate_player(player, EliminationType.NIGHT_KILL)
            
            werewolf_elimination_event = Event(
                type=EventType.WEREWOLF_ELIMINATION,
                eliminated_player=player,
                description=rationale
            )
            self.game.log_event(game_state.current_round, werewolf_elimination_event)
            
            game_state.latest_werewolf_kill = (player, EliminationStatus.SUCCESS)

    async def execute_seer_investigation(self):
        game_state = self.game.state
        seer = game_state.seer

        # Check if seer is still alive
        if seer is None:
            await self.game.log("[Night] Seer is dead, skipping investigation")
            return

        await self.game.log(f"[Night] Seer {seer.id[:8]} choosing target...")
        response = await seer.talk_to_agent(
            prompt=seer.get_seer_prompt(),
        )

        player = response["player_id"]
        rationale = response["reason"]

        seer_investigation_event = Event(
            type=EventType.SEER_INVESTIGATION,
            player=seer.id,
            description=rationale
        )

        self.game.log_event(game_state.current_round, seer_investigation_event)

        # Reveal investigation result to seer - check both primary and secondary werewolf
        is_werewolf = False
        if game_state.primary_werewolf is not None and game_state.primary_werewolf.id == player:
            is_werewolf = True
        elif game_state.secondary_werewolf is not None and game_state.secondary_werewolf.id == player:
            is_werewolf = True
        await self.game.log(f"[Night] Seer investigated {player[:8]}: {'WEREWOLF' if is_werewolf else 'not werewolf'}")

        # Store the seer check for future reference
        # Note: For LLM participants, they don't have persistent memory so we skip the reveal call
        # The seer_checks list is used to include this info in future prompts
        game_state.seer_checks.append((player, is_werewolf))