import pytest
from unittest.mock import Mock, AsyncMock

from src.phases.voting import Voting
from src.models.Vote import Vote
from src.models.enum.EventType import EventType
from src.models.Message import Message


class TestVotingPhase:
    """Test suite for the Voting phase."""

    @pytest.mark.asyncio
    async def test_voting_phase_initialization(self, mock_game, mock_messenger):
        """Test that voting phase initializes correctly."""
        voting = Voting(mock_game, mock_messenger)

        assert voting.game == mock_game
        assert voting.messenger == mock_messenger

    @pytest.mark.asyncio
    async def test_voting_phase_complete_flow(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that voting phase executes complete flow: collect votes and eliminate."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = vote_response

        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.run()

        # Verify votes were collected from all participants
        total_calls = sum(p.talk_to_agent.call_count for p in sample_participants.values())
        assert total_calls == len(sample_participants)

        # Verify elimination occurred
        mock_game.state.eliminate_player.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_round_votes(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that votes are collected from all active participants."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = vote_response

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify all participants were asked to vote
        for participant in sample_participants.values():
            participant.talk_to_agent.assert_called_once()
            participant.get_vote_prompt.assert_called_once()

        # Verify votes were stored
        assert len(mock_game.state.votes[1]) == len(sample_participants)

        # Verify events were logged
        assert mock_game.log_event.call_count == len(sample_participants)

    def test_tally_and_eliminate_simple_majority(self, mock_game, mock_messenger):
        """Test that player with most votes is eliminated."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_game.state.current_round = 1

        # Create votes where villager_2 gets 3 votes, others get fewer
        mock_game.state.votes = {1: [
            Vote(voter_id="werewolf_1", voted_for_id="villager_2", rationale="Suspicious"),
            Vote(voter_id="seer_1", voted_for_id="villager_2", rationale="Seems guilty"),
            Vote(voter_id="villager_1", voted_for_id="villager_2", rationale="Agree"),
            Vote(voter_id="villager_2", voted_for_id="villager_1", rationale="Self defense"),
            Vote(voter_id="villager_3", voted_for_id="villager_1", rationale="Not sure")
        ]}

        # Execute
        voting.tally_and_eliminate()

        # Verify villager_2 was eliminated (most votes)
        mock_game.state.eliminate_player.assert_called_once()
        eliminated_player = mock_game.state.eliminate_player.call_args[0][0]
        assert eliminated_player == "villager_2"

    def test_tally_and_eliminate_tie_handling(self, mock_game, mock_messenger):
        """Test that ties are handled (first player with max votes is eliminated)."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_game.state.current_round = 1

        # Create tie scenario
        mock_game.state.votes = {1: [
            Vote(voter_id="werewolf_1", voted_for_id="villager_1", rationale="Suspicious"),
            Vote(voter_id="seer_1", voted_for_id="villager_1", rationale="Seems guilty"),
            Vote(voter_id="villager_1", voted_for_id="villager_2", rationale="Self defense"),
            Vote(voter_id="villager_2", voted_for_id="villager_1", rationale="Counter"),
            Vote(voter_id="villager_3", voted_for_id="villager_2", rationale="Not sure")
        ]}

        # Execute
        voting.tally_and_eliminate()

        # Verify someone was eliminated
        mock_game.state.eliminate_player.assert_called_once()

    @pytest.mark.asyncio
    async def test_voting_logs_events(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that voting phase logs all vote events."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = vote_response

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify events were logged for each vote
        logged_events = [call.args[1] for call in mock_game.log_event.call_args_list]
        vote_events = [e for e in logged_events if e.type == EventType.VOTE]

        assert len(vote_events) == len(sample_participants)

    @pytest.mark.asyncio
    async def test_voting_with_fewer_participants(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that only active players vote (eliminated players excluded)."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        # Only use subset of participants
        active_participants = [
            sample_participants["werewolf"],
            sample_participants["seer"],
            sample_participants["villager2"],
            sample_participants["villager3"]
        ]

        for participant in active_participants:
            participant.talk_to_agent.return_value = vote_response

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: active_participants}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify only active participants voted
        total_calls = sum(p.talk_to_agent.call_count for p in active_participants)
        assert total_calls == len(active_participants)
        assert len(mock_game.state.votes[1]) == len(active_participants)
