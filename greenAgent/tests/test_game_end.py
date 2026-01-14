import pytest
from unittest.mock import Mock, patch

from src.phases.game_end import GameEnd


class TestGameEndPhase:
    """Test suite for the Game End phase."""

    @pytest.mark.asyncio
    async def test_game_end_phase_initialization(self, mock_game, mock_messenger):
        """Test that game end phase initializes correctly."""
        game_end = GameEnd(mock_game, mock_messenger)

        assert game_end.game == mock_game
        assert game_end.messenger == mock_messenger

    @pytest.mark.asyncio
    async def test_game_end_phase_run(self, mock_game, mock_messenger):
        """Test that game end phase run method executes and returns analytics."""
        game_end = GameEnd(mock_game, mock_messenger)

        with patch('src.phases.game_end.compute_game_analytics') as mock_analytics:
            with patch('src.phases.game_end.render_summary_text') as mock_render:
                mock_analytics.return_value = {
                    "winner": "villagers",
                    "rounds": 3
                }
                mock_render.return_value = "Game summary text"

                # Execute
                result = await game_end.run()

                # Verify
                mock_analytics.assert_called_once_with(mock_game.state)
                mock_render.assert_called_once()
                assert "summary_text" in result
                assert result["winner"] == "villagers"

    @pytest.mark.asyncio
    async def test_game_end_returns_analytics_dict(self, mock_game, mock_messenger):
        """Test that game end returns a dictionary with analytics."""
        game_end = GameEnd(mock_game, mock_messenger)

        with patch('src.phases.game_end.compute_game_analytics') as mock_analytics:
            with patch('src.phases.game_end.render_summary_text') as mock_render:
                mock_analytics.return_value = {
                    "winner": "werewolves",
                    "rounds": 5,
                    "eliminations": ["player1", "player2"]
                }
                mock_render.return_value = "The werewolves won!"

                result = await game_end.run()

                assert isinstance(result, dict)
                assert "summary_text" in result
                assert result["summary_text"] == "The werewolves won!"
