import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from src.models.Participant import Participant
from src.models.enum.Role import Role
from src.models.Message import Message
from src.models.Event import Event
from src.models.Vote import Vote
from src.models.Bid import Bid
from src.game.Game import Game
from src.game.GameData import GameData
from src.a2a.messenger import Messenger


@pytest.fixture
def mock_messenger():
    """Create a mock messenger for testing."""
    messenger = Mock(spec=Messenger)
    messenger.talk_to_agent = AsyncMock()
    messenger.reset = Mock()
    return messenger


@pytest.fixture
def mock_game_data():
    """Create a mock game data for participants."""
    game_data = Mock(spec=GameData)
    game_data.current_round = 1
    game_data.winner = None
    game_data.turns_to_speak_per_round = 1
    game_data.participants = {}
    game_data.speaking_order = {}
    game_data.chat_history = {}
    game_data.bids = {}
    game_data.votes = {}
    game_data.eliminations = {}
    game_data.events = {}
    game_data.seer_checks = []
    game_data.latest_werewolf_kill = None
    return game_data


def create_mock_participant(id: str, role: Role, game_data, messenger, url: str = None, use_llm: bool = True):
    """Helper to create a mock participant with talk_to_agent mocked."""
    participant = Mock(spec=Participant)
    participant.id = id
    participant.role = role
    participant.game_data = game_data
    participant.use_llm = use_llm
    participant.messenger = messenger
    participant.url = url
    participant.llm = None
    participant.llm_state = None

    # Mock the async talk_to_agent method
    participant.talk_to_agent = AsyncMock()

    # Mock prompt methods
    participant.get_bid_prompt = Mock(return_value="bid prompt")
    participant.get_debate_prompt = Mock(return_value="debate prompt")
    participant.get_vote_prompt = Mock(return_value="vote prompt")
    participant.get_werewolf_prompt = Mock(return_value="werewolf prompt")
    participant.get_seer_prompt = Mock(return_value="seer prompt")
    participant.get_seer_reveal_prompt = Mock(return_value="seer reveal prompt")

    return participant


@pytest.fixture
def sample_participants(mock_game_data, mock_messenger):
    """Create a set of sample participants for testing."""
    participants = {
        "werewolf": create_mock_participant(
            id="werewolf_1",
            role=Role.WEREWOLF,
            game_data=mock_game_data,
            messenger=mock_messenger,
            url="http://localhost:8001",
            use_llm=False
        ),
        "seer": create_mock_participant(
            id="seer_1",
            role=Role.SEER,
            game_data=mock_game_data,
            messenger=mock_messenger,
            url="http://localhost:8002",
            use_llm=True
        ),
        "villager1": create_mock_participant(
            id="villager_1",
            role=Role.VILLAGER,
            game_data=mock_game_data,
            messenger=mock_messenger,
            url="http://localhost:8003",
            use_llm=True
        ),
        "villager2": create_mock_participant(
            id="villager_2",
            role=Role.VILLAGER,
            game_data=mock_game_data,
            messenger=mock_messenger,
            url="http://localhost:8004",
            use_llm=True
        ),
        "villager3": create_mock_participant(
            id="villager_3",
            role=Role.VILLAGER,
            game_data=mock_game_data,
            messenger=mock_messenger,
            url="http://localhost:8005",
            use_llm=True
        ),
    }

    # Update game_data with participants
    participants_list = list(participants.values())
    mock_game_data.participants = {1: participants_list}
    mock_game_data.speaking_order = {1: [p.id for p in participants_list]}
    mock_game_data.werewolf = participants["werewolf"]
    mock_game_data.seer = participants["seer"]
    mock_game_data.villagers = [participants["villager1"], participants["villager2"], participants["villager3"]]

    return participants


@pytest.fixture
def mock_game(sample_participants, mock_messenger, mock_game_data):
    """Create a mock game instance with initialized state."""
    game = Mock(spec=Game)

    # Use mock_game_data as state
    mock_game_data.eliminate_player = Mock()
    mock_game_data.votes = {1: []}
    mock_game_data.chat_history = {1: []}
    mock_game_data.bids = {}

    game.state = mock_game_data
    game.messenger = mock_messenger
    game.log_event = Mock()
    return game


@pytest.fixture
def werewolf_elimination_response():
    """Sample parsed response for werewolf elimination."""
    return {"player_id": "villager_1", "reason": "They seem suspicious and are deflecting attention."}


@pytest.fixture
def seer_investigation_response():
    """Sample parsed response for seer investigation."""
    return {"player_id": "werewolf_1", "reason": "I want to check if they are the werewolf based on their behavior."}


@pytest.fixture
def vote_response():
    """Sample parsed response for voting."""
    return {"player_id": "villager_2", "reason": "Based on the discussion, I believe they are most likely the werewolf."}


@pytest.fixture
def bid_response():
    """Sample parsed response for bidding."""
    return {"bid_amount": 50, "reason": "I have important information to share."}


@pytest.fixture
def debate_message_response():
    """Sample parsed response for debate message."""
    return {"message": "I think we should carefully consider all the evidence before voting."}


@pytest.fixture
def agent_url():
    """Default agent URL for testing."""
    return "http://localhost:9999"
