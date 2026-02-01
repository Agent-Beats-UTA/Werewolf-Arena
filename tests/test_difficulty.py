import pytest
from src.models.enum.Difficulty import Difficulty
from src.services.llm import LLM


class TestDifficultyEnum:
    """Test suite for Difficulty enum."""

    def test_difficulty_enum_values(self):
        """Test that difficulty enum has expected values."""
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.HARD.value == "hard"

    def test_difficulty_get_model_easy(self):
        """Test that easy difficulty returns correct model."""
        model = Difficulty.EASY.get_model()
        assert model == "gemini-1.5-flash"

    def test_difficulty_get_model_hard(self):
        """Test that hard difficulty returns correct model."""
        model = Difficulty.HARD.get_model()
        assert model == "gemini-2.0-flash"

    def test_difficulty_default_is_hard(self):
        """Test that default model defaults to hard (2.0)."""
        # Using unknown difficulty should default to hard
        assert Difficulty.HARD.get_model() == "gemini-2.0-flash"


class TestLLMDifficulty:
    """Test suite for LLM difficulty integration."""

    def test_llm_easy_difficulty(self):
        """Test that LLM initializes with easy difficulty model."""
        llm = LLM(difficulty=Difficulty.EASY)
        assert llm.difficulty == Difficulty.EASY
        assert llm.model == "gemini-1.5-flash"

    def test_llm_hard_difficulty(self):
        """Test that LLM initializes with hard difficulty model."""
        llm = LLM(difficulty=Difficulty.HARD)
        assert llm.difficulty == Difficulty.HARD
        assert llm.model == "gemini-2.0-flash"

    def test_llm_default_difficulty(self):
        """Test that LLM defaults to hard difficulty."""
        llm = LLM()
        assert llm.difficulty == Difficulty.HARD
        assert llm.model == "gemini-2.0-flash"

    def test_llm_preserves_difficulty_on_init(self):
        """Test that LLM preserves difficulty setting through initialization."""
        for difficulty in [Difficulty.EASY, Difficulty.HARD]:
            llm = LLM(difficulty=difficulty)
            assert llm.difficulty == difficulty
            assert llm.model == difficulty.get_model()


class TestParticipantDifficulty:
    """Test suite for Participant difficulty integration."""

    def test_participant_difficulty_easy(self, mock_game_data, mock_messenger):
        """Test that participant can be created with easy difficulty."""
        from src.models.Participant import Participant
        from src.models.enum.Role import Role

        participant = Participant(
            id="test_1",
            role=Role.VILLAGER,
            game_data=mock_game_data,
            use_llm=True,
            messenger=mock_messenger,
            llm=LLM(difficulty=Difficulty.EASY),
            difficulty=Difficulty.EASY
        )
        assert participant.difficulty == Difficulty.EASY

    def test_participant_difficulty_hard(self, mock_game_data, mock_messenger):
        """Test that participant can be created with hard difficulty."""
        from src.models.Participant import Participant
        from src.models.enum.Role import Role

        participant = Participant(
            id="test_1",
            role=Role.VILLAGER,
            game_data=mock_game_data,
            use_llm=True,
            messenger=mock_messenger,
            llm=LLM(difficulty=Difficulty.HARD),
            difficulty=Difficulty.HARD
        )
        assert participant.difficulty == Difficulty.HARD


class TestEvalRequestDifficulty:
    """Test suite for EvalRequest difficulty parameter."""

    def test_eval_request_with_easy_difficulty(self):
        """Test EvalRequest with easy difficulty."""
        from src.models.EvalRequest import EvalRequest

        request_data = {
            "participants": {
                "agent1": "http://localhost:8001"
            },
            "difficulty": "easy"
        }
        request = EvalRequest.model_validate(request_data)
        assert request.difficulty == Difficulty.EASY

    def test_eval_request_with_hard_difficulty(self):
        """Test EvalRequest with hard difficulty."""
        from src.models.EvalRequest import EvalRequest

        request_data = {
            "participants": {
                "agent1": "http://localhost:8001"
            },
            "difficulty": "hard"
        }
        request = EvalRequest.model_validate(request_data)
        assert request.difficulty == Difficulty.HARD

    def test_eval_request_defaults_to_hard(self):
        """Test that EvalRequest defaults to hard difficulty."""
        from src.models.EvalRequest import EvalRequest

        request_data = {
            "participants": {
                "agent1": "http://localhost:8001"
            }
        }
        request = EvalRequest.model_validate(request_data)
        assert request.difficulty == Difficulty.HARD

    def test_eval_request_from_json(self):
        """Test EvalRequest parsing from JSON."""
        from src.models.EvalRequest import EvalRequest
        import json

        json_data = json.dumps({
            "participants": {
                "agent1": "http://localhost:8001"
            },
            "difficulty": "easy"
        })
        request = EvalRequest.model_validate_json(json_data)
        assert request.difficulty == Difficulty.EASY