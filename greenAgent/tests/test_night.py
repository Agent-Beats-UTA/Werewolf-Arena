import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from src.phases.night import Night
from src.models.enum.EventType import EventType
from src.models.enum.EliminationType import EliminationType


class TestNightPhase:
    """Test suite for the Night phase."""

    @pytest.mark.asyncio
    async def test_night_phase_complete_flow(self, mock_game, mock_messenger, werewolf_elimination_response, seer_investigation_response):
        """Test that the night phase executes both werewolf kill and seer investigation."""
        # Setup
        night = Night(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.side_effect = [
            werewolf_elimination_response,  # Werewolf kill response
            seer_investigation_response,     # Seer investigation response
            "Investigation complete"         # Seer reveal response
        ]

        # Execute
        await night.run()

        # Verify werewolf action was called
        assert mock_messenger.talk_to_agent.call_count == 3
        # Verify events were logged
        assert mock_game.log_event.call_count >= 2

    @pytest.mark.asyncio
    async def test_werewolf_kill_execution(self, mock_game, mock_messenger, werewolf_elimination_response):
        """Test that werewolf successfully eliminates a player."""
        # Setup
        night = Night(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.return_value = werewolf_elimination_response

        # Execute
        await night.execute_werewolf_kill()

        # Verify
        mock_messenger.talk_to_agent.assert_called_once()
        call_args = mock_messenger.talk_to_agent.call_args
        assert call_args.kwargs['url'] == mock_game.state.werewolf.url
        assert 'YOU ARE THE WEREWOLF' in call_args.kwargs['message']

        # Verify elimination was logged with correct elimination type
        mock_game.state.eliminate_player.assert_called_once_with('villager_1', EliminationType.NIGHT_KILL)

    @pytest.mark.asyncio
    async def test_seer_investigation_execution(self, mock_game, mock_messenger, seer_investigation_response):
        """Test that seer successfully investigates a player."""
        # Setup
        night = Night(mock_game, mock_messenger)
        mock_game.state.seer_checks = []
        mock_messenger.talk_to_agent.side_effect = [
            seer_investigation_response,  # Investigation choice
            "Investigation complete"       # Investigation result
        ]

        # Execute
        await night.execute_seer_investigation()

        # Verify
        assert mock_messenger.talk_to_agent.call_count == 2
        first_call = mock_messenger.talk_to_agent.call_args_list[0]
        assert first_call.kwargs['url'] == mock_game.state.seer.url
        assert 'YOU ARE THE SEER' in first_call.kwargs['message']

    def test_parse_json_response_valid_json(self, mock_game, mock_messenger):
        """Test parsing a valid JSON response."""
        night = Night(mock_game, mock_messenger)
        valid_json = '{"player_id": "test_player", "reason": "test reason"}'

        result = night._parse_json_response(valid_json)

        assert result['player_id'] == 'test_player'
        assert result['reason'] == 'test reason'

    def test_parse_json_response_with_markdown(self, mock_game, mock_messenger):
        """Test parsing JSON wrapped in markdown code blocks."""
        night = Night(mock_game, mock_messenger)
        markdown_json = '''```json
{
    "player_id": "test_player",
    "reason": "test reason"
}
```'''

        result = night._parse_json_response(markdown_json)

        assert result['player_id'] == 'test_player'
        assert result['reason'] == 'test reason'

    def test_parse_json_response_invalid_json(self, mock_game, mock_messenger):
        """Test that invalid JSON raises an error."""
        night = Night(mock_game, mock_messenger)
        invalid_json = 'This is not JSON'

        with pytest.raises(ValueError, match="Could not parse JSON"):
            night._parse_json_response(invalid_json)

    def test_is_werewolf_check(self, mock_game, mock_messenger):
        """Test werewolf identification."""
        night = Night(mock_game, mock_messenger)

        assert night.is_werewolf('werewolf_1') is True
        assert night.is_werewolf('villager_1') is False

    def test_werewolf_prompt_format(self, mock_game, mock_messenger):
        """Test that werewolf prompt is properly formatted."""
        night = Night(mock_game, mock_messenger)
        participants = ['villager_1', 'villager_2', 'seer_1']

        prompt = night.get_werewolf_prompt(round_num=1, participants=participants)

        assert 'ROUND 1' in prompt
        assert 'YOU ARE THE WEREWOLF' in prompt
        assert 'villager_1' in prompt
        assert 'villager_2' in prompt
        assert 'seer_1' in prompt
        assert 'player_id' in prompt
        assert 'reason' in prompt

    def test_seer_prompt_format(self, mock_game, mock_messenger):
        """Test that seer prompt is properly formatted."""
        night = Night(mock_game, mock_messenger)
        participants = ['villager_1', 'villager_2', 'werewolf_1']
        previous_checks = [('villager_1', False)]

        prompt = night.get_seer_prompt(
            round_num=1,
            participants=participants,
            previous_checks=previous_checks
        )

        assert 'ROUND 1' in prompt
        assert 'YOU ARE THE SEER' in prompt
        assert 'villager_2' in prompt  # Should appear in unchecked list
        assert 'werewolf_1' in prompt
        assert 'villager_1 is werewolf: False' in prompt  # Should appear in checked list

    def test_seer_reveal_prompt_werewolf_found(self, mock_game, mock_messenger):
        """Test seer reveal prompt when werewolf is found."""
        night = Night(mock_game, mock_messenger)

        prompt = night.get_seer_reveal_prompt(player_id='werewolf_1', is_werewolf=True)

        assert 'werewolf_1' in prompt
        assert 'are the werewolf' in prompt

    def test_seer_reveal_prompt_innocent_player(self, mock_game, mock_messenger):
        """Test seer reveal prompt when player is innocent."""
        night = Night(mock_game, mock_messenger)

        prompt = night.get_seer_reveal_prompt(player_id='villager_1', is_werewolf=False)

        assert 'villager_1' in prompt
        assert 'are not the werewolf' in prompt

    @pytest.mark.asyncio
    async def test_night_phase_logs_events(self, mock_game, mock_messenger, werewolf_elimination_response, seer_investigation_response):
        """Test that night phase logs all required events."""
        # Setup
        night = Night(mock_game, mock_messenger)
        mock_messenger.talk_to_agent.side_effect = [
            werewolf_elimination_response,
            seer_investigation_response,
            "Investigation complete"
        ]

        # Execute
        await night.run()

        # Verify events were logged
        # log_event signature is (round, event), so event is at args[1]
        logged_events = [call.args[1] for call in mock_game.log_event.call_args_list]

        # Should have werewolf elimination, seer investigation, and night end events
        assert any(event.type == EventType.WEREWOLF_ELIMINATION for event in logged_events)
        assert any(event.type == EventType.SEER_INVESTIGATION for event in logged_events)
        assert any(event.type == EventType.NIGHT_END for event in logged_events)
