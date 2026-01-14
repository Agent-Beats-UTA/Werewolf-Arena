import pytest
from unittest.mock import Mock, AsyncMock

from src.phases.night import Night
from src.models.enum.EventType import EventType
from src.models.enum.EliminationType import EliminationType


class TestNightPhase:
    """Test suite for the Night phase."""

    @pytest.mark.asyncio
    async def test_night_phase_initialization(self, mock_game, mock_messenger):
        """Test that night phase initializes correctly."""
        night = Night(mock_game, mock_messenger)

        assert night.game == mock_game
        assert night.messenger == mock_messenger

    @pytest.mark.asyncio
    async def test_night_phase_complete_flow(self, mock_game, mock_messenger, werewolf_elimination_response, seer_investigation_response, sample_participants):
        """Test that the night phase executes both werewolf kill and seer investigation."""
        # Setup
        night = Night(mock_game, mock_messenger)

        werewolf = sample_participants["werewolf"]
        seer = sample_participants["seer"]

        werewolf.talk_to_agent.return_value = werewolf_elimination_response
        seer.talk_to_agent.side_effect = [
            seer_investigation_response,  # Investigation choice
            {}  # Investigation reveal (no response needed)
        ]

        mock_game.state.werewolf = werewolf
        mock_game.state.seer = seer

        # Execute
        await night.run()

        # Verify werewolf and seer were called
        werewolf.talk_to_agent.assert_called_once()
        assert seer.talk_to_agent.call_count == 2  # Investigation + reveal

        # Verify events were logged
        assert mock_game.log_event.call_count >= 2

    @pytest.mark.asyncio
    async def test_werewolf_kill_execution(self, mock_game, mock_messenger, werewolf_elimination_response, sample_participants):
        """Test that werewolf successfully eliminates a player."""
        # Setup
        night = Night(mock_game, mock_messenger)

        werewolf = sample_participants["werewolf"]
        werewolf.talk_to_agent.return_value = werewolf_elimination_response

        mock_game.state.werewolf = werewolf

        # Execute
        await night.execute_werewolf_kill()

        # Verify
        werewolf.talk_to_agent.assert_called_once()
        werewolf.get_werewolf_prompt.assert_called_once()

        # Verify elimination was logged with correct elimination type
        mock_game.state.eliminate_player.assert_called_once_with('villager_1', EliminationType.NIGHT_KILL)

    @pytest.mark.asyncio
    async def test_seer_investigation_execution(self, mock_game, mock_messenger, seer_investigation_response, sample_participants):
        """Test that seer successfully investigates a player."""
        # Setup
        night = Night(mock_game, mock_messenger)

        seer = sample_participants["seer"]
        werewolf = sample_participants["werewolf"]

        seer.talk_to_agent.side_effect = [
            seer_investigation_response,  # Investigation choice
            {}  # Investigation reveal
        ]

        mock_game.state.seer = seer
        mock_game.state.werewolf = werewolf
        mock_game.state.seer_checks = []

        # Execute
        await night.execute_seer_investigation()

        # Verify
        assert seer.talk_to_agent.call_count == 2
        seer.get_seer_prompt.assert_called_once()
        seer.get_seer_reveal_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_night_phase_logs_events(self, mock_game, mock_messenger, werewolf_elimination_response, seer_investigation_response, sample_participants):
        """Test that night phase logs all required events."""
        # Setup
        night = Night(mock_game, mock_messenger)

        werewolf = sample_participants["werewolf"]
        seer = sample_participants["seer"]

        werewolf.talk_to_agent.return_value = werewolf_elimination_response
        seer.talk_to_agent.side_effect = [
            seer_investigation_response,
            {}
        ]

        mock_game.state.werewolf = werewolf
        mock_game.state.seer = seer

        # Execute
        await night.run()

        # Verify events were logged
        logged_events = [call.args[1] for call in mock_game.log_event.call_args_list]

        # Should have werewolf elimination, seer investigation, and night end events
        assert any(event.type == EventType.WEREWOLF_ELIMINATION for event in logged_events)
        assert any(event.type == EventType.SEER_INVESTIGATION for event in logged_events)
        assert any(event.type == EventType.NIGHT_END for event in logged_events)

    @pytest.mark.asyncio
    async def test_werewolf_kill_updates_latest_kill(self, mock_game, mock_messenger, werewolf_elimination_response, sample_participants):
        """Test that werewolf kill updates the latest_werewolf_kill state."""
        # Setup
        night = Night(mock_game, mock_messenger)

        werewolf = sample_participants["werewolf"]
        werewolf.talk_to_agent.return_value = werewolf_elimination_response

        mock_game.state.werewolf = werewolf
        mock_game.state.latest_werewolf_kill = None

        # Execute
        await night.execute_werewolf_kill()

        # Verify latest kill was updated
        assert mock_game.state.latest_werewolf_kill == "villager_1"
