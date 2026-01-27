from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from src.models.enum.EliminationType import EliminationType
from src.models.Message import Message
from src.models.Vote import Vote
from src.models.Elimination import Elimination
from src.models.Event import Event
from src.models.Bid import Bid

from src.models.enum.Role import Role
from src.models.Participant import Participant

class GameData(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    current_round: int
    winner: Optional[str] = None
    turns_to_speak_per_round: int
    participants: Dict[int, List[Any]] = {}  # List[Participant] at runtime
    primary_werewolf: Optional[Participant] = None
    secondary_werewolf: Optional[Participant] = None
    seer: Optional[Participant] = None
    doctor: Optional[Participant] = None
    villagers: List[Participant] = []  # List[Participant] at runtime
    speaking_order: Dict[int, List[str]] = {}
    chat_history: Dict[int, List[Message]] = {}
    bids: Dict[int, List[Bid]] = {}
    votes: Dict[int, List[Vote]] = {}
    eliminations: Dict[int, List[Elimination]] = {}
    events: Dict[int, List[Event]] = {}
    seer_checks: List[tuple] = []
    doctor_saves: Dict[int, str] = {}
    latest_werewolf_kill: Optional[tuple] = None

    def set_status(self, status: str):  # assignment | player_actions | bidding | discussion | voting | end | reset
        pass

    def declare_winner(self, winner: str):
        self.winner = winner

    def place_bid(self, participant_id: str, bid_amount: int):
        pass

    def cast_vote(self, voter: str, voting_for: str, rationale: str):
        vote = Vote(voter_id=voter, voted_for_id=voting_for, rationale=rationale)
        if self.current_round not in self.votes:
            self.votes[self.current_round] = []
        self.votes[self.current_round].append(vote)

    def add_participant(self, participant_id: str, url: str):
        # Add participant to round 1's participant list
        participant = Participant(id=participant_id, url=url, role=Role.VILLAGER)
        if 1 not in self.participants:
            self.participants[1] = []
        self.participants[1].append(participant)

    def assign_role_to_participant(self, participant_id: str, role: str):
        # Find and update the participant in round 1 (initial setup)
        if 1 in self.participants:
            for participant in self.participants[1]:
                if participant.id == participant_id:
                    participant.role = getattr(Role, role.upper())
                    break

    def eliminate_player(self, participant_id: str, elimination_type: EliminationType = EliminationType.VOTED_OUT):
        """
        Eliminate a player from the current round.

        Removes the player from the current round's participant list and tracks the elimination.
        Also clears special role references (werewolf, seer, doctor) if the eliminated player held that role.
        If the primary werewolf is eliminated, the secondary werewolf is promoted to primary.

        Args:
            participant_id: The ID of the participant to eliminate
            elimination_type: Type of elimination (VOTED_OUT or NIGHT_KILL)
        """
        current_participants = self.participants.get(self.current_round, [])

        # Handle werewolf elimination with promotion logic
        if self.primary_werewolf is not None and self.primary_werewolf.id == participant_id:
            # Primary werewolf eliminated - promote secondary to primary
            self.primary_werewolf = self.secondary_werewolf
            self.secondary_werewolf = None
        elif self.secondary_werewolf is not None and self.secondary_werewolf.id == participant_id:
            # Secondary werewolf eliminated
            self.secondary_werewolf = None

        # Clear other special role references if this player held that role
        if self.seer is not None and self.seer.id == participant_id:
            self.seer = None
        if self.doctor is not None and self.doctor.id == participant_id:
            self.doctor = None

        # Remove the participant from the current round's list
        self.participants[self.current_round] = [
            p for p in current_participants
            if p.id != participant_id
        ]

        # Add to eliminations tracking
        elimination = Elimination(
            eliminated_participant=participant_id,
            elimination_type=elimination_type
        )
        if self.current_round not in self.eliminations:
            self.eliminations[self.current_round] = []
        self.eliminations[self.current_round].append(elimination)

    def initialize_next_round(self):
        """
        Initialize the next round with current participants and reset round-specific data.

        This should be called at the end of a round (typically after round_end phase)
        to set up the next round.
        """
        next_round = self.current_round + 1

        # Copy current participants to next round (they're already filtered)
        current_participants = self.participants.get(self.current_round, [])
        self.participants[next_round] = current_participants.copy()

        # Initialize empty data structures for the new round
        # These will be populated during the respective phases
        self.chat_history[next_round] = []
        self.bids[next_round] = []
        self.votes[next_round] = []
        self.events[next_round] = []
        # speaking_order will be set during bidding phase
        # eliminations will be added as players are eliminated