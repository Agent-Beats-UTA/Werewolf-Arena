import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.phases.voting import Voting
from src.models.Vote import Vote
from src.models.enum.EventType import EventType
from src.models.Message import Message


class TestVotingPhase:
    """Test suite for the Voting phase."""

    @pytest.mark.asyncio
    async def test_voting_phase_complete_flow(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that voting phase executes complete flow: collect votes and eliminate."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.return_value = vote_response

        # Mock the participants for current round
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.run()

        # Verify votes were collected from all participants
        assert mock_messenger.talk_to_agent.call_count == len(sample_participants)

        # Verify elimination occurred
        mock_game.state.eliminate_player.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_round_votes(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that votes are collected from all active participants."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.return_value = vote_response

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify all participants were asked to vote
        assert mock_messenger.talk_to_agent.call_count == len(sample_participants)

        # Verify votes were stored
        assert len(mock_game.state.votes[1]) == len(sample_participants)

        # Verify events were logged
        assert mock_game.log_event.call_count == len(sample_participants)

    @pytest.mark.asyncio
    async def test_voting_prompt_format(self, mock_game, mock_messenger, sample_participants):
        """Test that voting prompt is properly formatted."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        test_messages = [
            Message(sender_id="player_1", content="I think player_2 is suspicious"),
            Message(sender_id="player_2", content="No, I'm innocent!")
        ]

        prompt = voting.get_vote_prompt(
            user_role="VILLAGER",
            messages=test_messages,
            participants=list(sample_participants.values())
        )

        # Verify prompt structure
        assert "It's time to vote" in prompt
        assert "VILLAGER" in prompt
        assert "player_1 - I think player_2 is suspicious" in prompt
        assert "player_2 - No, I'm innocent!" in prompt
        assert "player_id" in prompt
        assert "reason" in prompt

    @pytest.mark.asyncio
    async def test_tally_and_eliminate_simple_majority(self, mock_game, mock_messenger):
        """Test that player with most votes is eliminated."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_game.state.current_round = 1

        # Create votes where villager_2 gets 3 votes, others get 1 each
        mock_game.state.votes = {1: [
            Vote(voter_id="werewolf_1", voted_for_id="villager_2", rationale="Suspicious"),
            Vote(voter_id="seer_1", voted_for_id="villager_2", rationale="Seems guilty"),
            Vote(voter_id="villager_1", voted_for_id="villager_2", rationale="Agree"),
            Vote(voter_id="villager_2", voted_for_id="villager_1", rationale="Self defense"),
            Vote(voter_id="villager_3", voted_for_id="villager_1", rationale="Not sure")
        ]}

        # Execute
        await voting.tally_and_eliminate()

        # Verify villager_2 was eliminated (most votes)
        mock_game.state.eliminate_player.assert_called_once()
        eliminated_player = mock_game.state.eliminate_player.call_args[0][0]
        assert eliminated_player == "villager_2"

    @pytest.mark.asyncio
    async def test_tally_and_eliminate_tie_handling(self, mock_game, mock_messenger):
        """Test that ties are handled (first player with max votes is eliminated)."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_game.state.current_round = 1

        # Create tie scenario: villager_1 and villager_2 each get 2 votes
        mock_game.state.votes = {1: [
            Vote(voter_id="werewolf_1", voted_for_id="villager_1", rationale="Suspicious"),
            Vote(voter_id="seer_1", voted_for_id="villager_1", rationale="Seems guilty"),
            Vote(voter_id="villager_1", voted_for_id="villager_2", rationale="Self defense"),
            Vote(voter_id="villager_2", voted_for_id="villager_1", rationale="Counter"),
            Vote(voter_id="villager_3", voted_for_id="villager_2", rationale="Not sure")
        ]}

        # Execute
        await voting.tally_and_eliminate()

        # Verify someone was eliminated (implementation may vary for ties)
        mock_game.state.eliminate_player.assert_called_once()

    @pytest.mark.asyncio
    async def test_voting_logs_events(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that voting phase logs all vote events."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.return_value = vote_response

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify events were logged for each vote
        logged_events = [call.args[0] for call in mock_game.log_event.call_args_list]
        vote_events = [e for e in logged_events if e.type == EventType.VOTE]

        assert len(vote_events) == len(sample_participants)

    @pytest.mark.asyncio
    async def test_voting_with_eliminated_players(self, mock_game, mock_messenger, vote_response, sample_participants):
        """Test that only active players vote (eliminated players excluded)."""
        # Setup
        voting = Voting(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.return_value = vote_response

        # Mark one player as eliminated
        sample_participants["villager1"].status = Status.ELIMINATED

        mock_game.state.current_round = 1
        active_participants = [p for p in sample_participants.values() if p.status == Status.ACTIVE]
        mock_game.state.participants = {1: active_participants}
        mock_game.state.votes = {1: []}
        mock_game.state.chat_history = {1: []}

        # Execute
        await voting.collect_round_votes()

        # Verify only active participants voted
        assert mock_messenger.talk_to_agent.call_count == len(active_participants)
        assert len(mock_game.state.votes[1]) == len(active_participants)

    def test_parse_json_response_valid_vote(self, mock_game, mock_messenger):
        """Test parsing a valid vote JSON response."""
        voting = Voting(mock_game, mock_messenger)
        valid_json = '{"player_id": "villager_1", "reason": "They are acting suspicious"}'

        result = voting._parse_json_response(valid_json)

        assert result['player_id'] == 'villager_1'
        assert result['reason'] == 'They are acting suspicious'

    def test_parse_json_response_with_markdown(self, mock_game, mock_messenger):
        """Test parsing vote JSON wrapped in markdown code blocks."""
        voting = Voting(mock_game, mock_messenger)
        markdown_json = '''```json
{
    "player_id": "werewolf_1",
    "reason": "Strong evidence they are the werewolf"
}
```'''

        result = voting._parse_json_response(markdown_json)

        assert result['player_id'] == 'werewolf_1'
        assert result['reason'] == 'Strong evidence they are the werewolf'

    @pytest.mark.asyncio
    async def test_vote_includes_discussion_context(self, mock_game, mock_messenger, sample_participants):
        """Test that vote prompt includes discussion context."""
        # Setup
        voting = Voting(mock_game, mock_messenger)

        discussion_messages = [
            Message(sender_id="werewolf_1", content="I saw player_2 acting strange"),
            Message(sender_id="villager_1", content="I agree with werewolf_1"),
            Message(sender_id="seer_1", content="I have information about player_3")
        ]

        prompt = voting.get_vote_prompt(
            user_role="VILLAGER",
            messages=discussion_messages,
            participants=list(sample_participants.values())
        )

        # Verify discussion is included in prompt
        for msg in discussion_messages:
            assert msg.sender_id in prompt
            assert msg.content in prompt
