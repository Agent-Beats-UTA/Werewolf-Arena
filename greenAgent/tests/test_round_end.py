import pytest
from unittest.mock import Mock

from src.phases.round_end import RoundEnd
from src.models.enum.Phase import Phase
from src.models.enum.Role import Role


class TestRoundEndPhase:
    """Test suite for the Round End phase."""

    def test_round_end_phase_initialization(self, mock_game, mock_messenger):
        """Test that round end phase initializes correctly."""
        round_end = RoundEnd(mock_game, mock_messenger)

        assert round_end.game == mock_game
        assert round_end.messenger == mock_messenger

    @pytest.mark.asyncio
    async def test_round_end_phase_run(self, mock_game, mock_messenger, sample_participants):
        """Test that round end phase run method executes without errors."""
        round_end = RoundEnd(mock_game, mock_messenger)

        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.werewolf = sample_participants["werewolf"]
        mock_game.state.declare_winner = Mock()
        mock_game.state.initialize_next_round = Mock()

        # Execute - should not raise errors
        await round_end.run()

    @pytest.mark.asyncio
    async def test_round_end_villagers_win_when_werewolf_eliminated(self, mock_game, mock_messenger, sample_participants):
        """Test that villagers win when werewolf is eliminated."""
        round_end = RoundEnd(mock_game, mock_messenger)

        # Setup: werewolf is NOT in participants (eliminated)
        villagers_only = [
            sample_participants["seer"],
            sample_participants["villager1"],
            sample_participants["villager2"]
        ]

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: villagers_only}
        mock_game.state.werewolf = sample_participants["werewolf"]  # werewolf exists but not in participants
        mock_game.state.declare_winner = Mock()
        mock_game.current_phase = None

        # Execute
        round_end.check_win_conditions()

        # Verify villagers won
        mock_game.state.declare_winner.assert_called_once_with("villagers")
        assert mock_game.current_phase == Phase.GAME_END

    @pytest.mark.asyncio
    async def test_round_end_werewolves_win_when_equal_numbers(self, mock_game, mock_messenger, sample_participants):
        """Test that werewolves win when they equal or outnumber villagers."""
        round_end = RoundEnd(mock_game, mock_messenger)

        # Setup: 1 werewolf, 1 villager (werewolf wins)
        remaining = [
            sample_participants["werewolf"],
            sample_participants["villager1"]
        ]

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: remaining}
        mock_game.state.werewolf = sample_participants["werewolf"]
        mock_game.state.declare_winner = Mock()
        mock_game.current_phase = None

        # Execute
        round_end.check_win_conditions()

        # Verify werewolves won
        mock_game.state.declare_winner.assert_called_once_with("werewolves")
        assert mock_game.current_phase == Phase.GAME_END

    @pytest.mark.asyncio
    async def test_round_end_continues_game_when_no_win(self, mock_game, mock_messenger, sample_participants):
        """Test that game continues when no win condition is met."""
        round_end = RoundEnd(mock_game, mock_messenger)

        # Setup: werewolf alive, villagers outnumber
        mock_game.state.current_round = 1
        mock_game.state.participants = {1: list(sample_participants.values())}
        mock_game.state.werewolf = sample_participants["werewolf"]
        mock_game.state.declare_winner = Mock()
        mock_game.state.initialize_next_round = Mock()
        mock_game.current_phase = None

        # Execute
        round_end.check_win_conditions()

        # Verify game continues
        mock_game.state.declare_winner.assert_not_called()
        mock_game.state.initialize_next_round.assert_called_once()
        assert mock_game.current_phase == Phase.NIGHT
        assert mock_game.state.current_round == 2

    def test_is_werewolf_alive(self, mock_game, mock_messenger, sample_participants):
        """Test werewolf alive check."""
        round_end = RoundEnd(mock_game, mock_messenger)
        mock_game.state.werewolf = sample_participants["werewolf"]

        # Werewolf in participants
        participants_with_werewolf = list(sample_participants.values())
        assert round_end.is_werewolf_alive(participants_with_werewolf) is True

        # Werewolf not in participants
        participants_without_werewolf = [
            sample_participants["seer"],
            sample_participants["villager1"]
        ]
        assert round_end.is_werewolf_alive(participants_without_werewolf) is False

    def test_count_werewolves(self, mock_game, mock_messenger, sample_participants):
        """Test counting werewolves."""
        round_end = RoundEnd(mock_game, mock_messenger)

        participants = list(sample_participants.values())
        assert round_end.count_werewolves(participants) == 1

    def test_count_villagers(self, mock_game, mock_messenger, sample_participants):
        """Test counting villagers (including seer)."""
        round_end = RoundEnd(mock_game, mock_messenger)

        participants = list(sample_participants.values())
        # 3 villagers + 1 seer = 4
        assert round_end.count_villagers(participants) == 4

    @pytest.mark.asyncio
    async def test_round_end_with_no_participants(self, mock_game, mock_messenger):
        """Test that round end handles empty participants gracefully."""
        round_end = RoundEnd(mock_game, mock_messenger)

        mock_game.state.current_round = 1
        mock_game.state.participants = {1: []}
        mock_game.state.werewolf = None
        mock_game.state.declare_winner = Mock()

        # Execute - should not raise errors
        round_end.check_win_conditions()

        # No winner should be declared with no participants
        mock_game.state.declare_winner.assert_not_called()
