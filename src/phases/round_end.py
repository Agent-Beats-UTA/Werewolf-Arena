from typing import TYPE_CHECKING

from src.models.abstract.Phase import Phase
from src.models.Event import Event
from src.models.enum.EventType import EventType
from src.models.enum.Phase import Phase as PhaseEnum
from src.models.enum.Role import Role

if TYPE_CHECKING:
    from src.game.Game import Game
    from src.a2a.messenger import Messenger

class RoundEnd(Phase):
    def __init__(self, game: "Game", messenger: "Messenger"):
        super().__init__(game, messenger)
        
    async def run(self):
        await self.check_win_conditions()
        self.log_event(EventType.ROUND_END)
        
    #Check if the game is over
    async def check_win_conditions(self):
        game_state = self.game.state
        current_round = game_state.current_round
        current_participants = game_state.participants.get(current_round, [])

        if not current_participants:
            return

        werewolf_count = self.count_werewolves(current_participants)
        villager_count = self.count_villagers(current_participants)

        await self.game.log(f"[RoundEnd] Round {current_round}: {len(current_participants)} alive, {werewolf_count} werewolves, {villager_count} villagers")

        # Villagers win if all werewolves are eliminated
        if werewolf_count == 0:
            await self.game.log("[RoundEnd] VILLAGERS WIN! All werewolves have been eliminated.")
            game_state.declare_winner("villagers")
            self.game.current_phase = PhaseEnum.GAME_END

        # Werewolves win if they equal or outnumber the villagers
        elif werewolf_count >= villager_count:
            await self.game.log(f"[RoundEnd] WEREWOLVES WIN! Werewolves ({werewolf_count}) >= Villagers ({villager_count})")
            game_state.declare_winner("werewolf")
            self.game.current_phase = PhaseEnum.GAME_END
        else:
            await self.game.log(f"[RoundEnd] Advancing to round {current_round + 1}")
            game_state.initialize_next_round()  # Initialize next round data BEFORE incrementing
            game_state.current_round += 1
            self.game.current_phase = PhaseEnum.NIGHT
    
    #Check if any werewolf is alive (primary or secondary)
    def is_werewolf_alive(self, participants):
        # Check if primary werewolf is alive
        if self.game.state.primary_werewolf is not None:
            if any(p.id == self.game.state.primary_werewolf.id for p in participants):
                return True
        # Check if secondary werewolf is alive
        if self.game.state.secondary_werewolf is not None:
            if any(p.id == self.game.state.secondary_werewolf.id for p in participants):
                return True
        return False

    #Count werewolves alive
    def count_werewolves(self, participants):
        return sum(1 for p in participants if p.role == Role.WEREWOLF)

    #Count villagers (non-werewolf players)
    def count_villagers(self, participants):
        return sum(1 for p in participants if p.role in [Role.VILLAGER, Role.SEER, Role.DOCTOR])
    
    #end of round logging
    def log_event(self, event_type: EventType):
        game_state = self.game.state
        current_round = game_state.current_round
        event = Event(type=event_type)
        self.game.log_event(current_round, event)
    