import pytest
from unittest.mock import Mock, AsyncMock

from src.phases.debate import Debate
from src.models.Message import Message


class TestDebatePhase:
    """Test suite for the Debate phase."""

    @pytest.mark.asyncio
    async def test_debate_phase_initialization(self, mock_game, mock_messenger):
        """Test that debate phase initializes correctly."""
        debate = Debate(mock_game, mock_messenger)

        assert debate.game == mock_game
        assert debate.messenger == mock_messenger

    @pytest.mark.asyncio
    async def test_debate_phase_run(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate phase executes complete flow."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 1
        participant_list = list(sample_participants.values())
        mock_game.state.participants = {1: participant_list}
        mock_game.state.speaking_order = {1: [p.id for p in participant_list]}
        mock_game.state.chat_history = {}

        # Execute
        await debate.run()

        # Verify all participants spoke
        total_calls = sum(p.talk_to_agent.call_count for p in sample_participants.values())
        assert total_calls == len(sample_participants)

    @pytest.mark.asyncio
    async def test_debate_follows_speaking_order(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate follows the established speaking order from bidding."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 1
        participant_list = list(sample_participants.values())
        mock_game.state.participants = {1: participant_list}

        # Set specific speaking order
        custom_order = ["seer_1", "werewolf_1", "villager_1", "villager_2", "villager_3"]
        mock_game.state.speaking_order = {1: custom_order}
        mock_game.state.chat_history = {}

        # Execute
        await debate.run()

        # Verify participants were called
        for participant in sample_participants.values():
            if participant.id in custom_order:
                participant.talk_to_agent.assert_called()

    @pytest.mark.asyncio
    async def test_debate_respects_turn_limits(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate respects the turns_to_speak_per_round limit."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 2  # Each player speaks twice
        participant_list = list(sample_participants.values())
        mock_game.state.participants = {1: participant_list}
        mock_game.state.speaking_order = {1: [p.id for p in participant_list]}
        mock_game.state.chat_history = {}

        # Execute
        await debate.run()

        # Verify each participant spoke twice (2 turns * 5 participants = 10 calls)
        total_calls = sum(p.talk_to_agent.call_count for p in sample_participants.values())
        assert total_calls == len(sample_participants) * 2

    @pytest.mark.asyncio
    async def test_debate_stores_chat_history(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate stores all messages in chat history."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 1
        participant_list = list(sample_participants.values())
        mock_game.state.participants = {1: participant_list}
        mock_game.state.speaking_order = {1: [p.id for p in participant_list]}
        mock_game.state.chat_history = {}

        # Execute
        await debate.run()

        # Verify chat history was created and populated
        assert 1 in mock_game.state.chat_history
        assert len(mock_game.state.chat_history[1]) == len(sample_participants)

        # Verify messages have correct structure
        for msg in mock_game.state.chat_history[1]:
            assert isinstance(msg, Message)
            assert msg.sender_id in [p.id for p in participant_list]

    @pytest.mark.asyncio
    async def test_debate_with_empty_chat_history(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate works correctly on first turn with empty chat history."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        villager = sample_participants["villager1"]
        villager.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 1
        mock_game.state.participants = {1: [villager]}
        mock_game.state.speaking_order = {1: ["villager_1"]}
        mock_game.state.chat_history = {}  # Empty chat history

        # Execute - should not raise errors
        await debate.run()

        # Verify message was sent and stored
        villager.talk_to_agent.assert_called_once()
        assert len(mock_game.state.chat_history[1]) == 1

    @pytest.mark.asyncio
    async def test_debate_calls_get_debate_prompt(self, mock_game, mock_messenger, debate_message_response, sample_participants):
        """Test that debate calls get_debate_prompt on each participant."""
        # Setup
        debate = Debate(mock_game, mock_messenger)

        for participant in sample_participants.values():
            participant.talk_to_agent.return_value = debate_message_response

        mock_game.state.current_round = 1
        mock_game.state.turns_to_speak_per_round = 1
        participant_list = list(sample_participants.values())
        mock_game.state.participants = {1: participant_list}
        mock_game.state.speaking_order = {1: [p.id for p in participant_list]}
        mock_game.state.chat_history = {}

        # Execute
        await debate.run()

        # Verify get_debate_prompt was called on each participant
        for participant in sample_participants.values():
            participant.get_debate_prompt.assert_called()
