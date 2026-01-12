import pytest
from unittest.mock import AsyncMock, Mock

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
def sample_participants():
    """Create a set of sample participants for testing."""
    return {
        "werewolf": Participant(
            id="werewolf_1",
            url="http://localhost:8001",
            role=Role.WEREWOLF
        ),
        "seer": Participant(
            id="seer_1",
            url="http://localhost:8002",
            role=Role.SEER
        ),
        "villager1": Participant(
            id="villager_1",
            url="http://localhost:8003",
            role=Role.VILLAGER
        ),
        "villager2": Participant(
            id="villager_2",
            url="http://localhost:8004",
            role=Role.VILLAGER
        ),
        "villager3": Participant(
            id="villager_3",
            url="http://localhost:8005",
            role=Role.VILLAGER
        ),
    }


@pytest.fixture
def game_state(sample_participants):
    """Create a basic game state for testing."""
    # participants is a dict mapping round number to list of participants
    participants_list = list(sample_participants.values())

    state = GameData(
        current_round=1,
        winner=None,
        turns_to_speak_per_round=1,
        participants={1: participants_list},
        werewolf=sample_participants["werewolf"],
        seer=sample_participants["seer"],
        villagers=[
            sample_participants["villager1"],
            sample_participants["villager2"],
            sample_participants["villager3"]
        ],
        speaking_order={1: [p.id for p in sample_participants.values()]},
        chat_history={},
        bids={},
        votes={},
        eliminations={},
        events={},
        seer_checks=[]
    )
    return state


@pytest.fixture
def mock_game(game_state, mock_messenger):
    """Create a mock game instance with initialized state."""
    game = Mock(spec=Game)

    # Create a mock state that has all the attributes from game_state
    # but allows us to mock methods
    mock_state = Mock()
    mock_state.current_round = game_state.current_round
    mock_state.winner = game_state.winner
    mock_state.turns_to_speak_per_round = game_state.turns_to_speak_per_round
    mock_state.participants = game_state.participants
    mock_state.werewolf = game_state.werewolf
    mock_state.seer = game_state.seer
    mock_state.villagers = game_state.villagers
    mock_state.speaking_order = game_state.speaking_order
    mock_state.chat_history = game_state.chat_history
    mock_state.bids = game_state.bids
    mock_state.votes = game_state.votes
    mock_state.eliminations = game_state.eliminations
    mock_state.events = game_state.events
    mock_state.seer_checks = game_state.seer_checks
    mock_state.latest_werewolf_kill = getattr(game_state, 'latest_werewolf_kill', None)
    mock_state.eliminate_player = Mock()

    game.state = mock_state
    game.messenger = mock_messenger
    game.log_event = Mock()
    return game


@pytest.fixture
def werewolf_elimination_response():
    """Sample JSON response for werewolf elimination."""
    return '{"player_id": "villager_1", "reason": "They seem suspicious and are deflecting attention."}'


@pytest.fixture
def seer_investigation_response():
    """Sample JSON response for seer investigation."""
    return '{"player_id": "werewolf_1", "reason": "I want to check if they are the werewolf based on their behavior."}'


@pytest.fixture
def vote_response():
    """Sample JSON response for voting."""
    return '{"player_id": "villager_2", "reason": "Based on the discussion, I believe they are most likely the werewolf."}'


@pytest.fixture
def bid_response():
    """Sample JSON response for bidding."""
    return '{"bid_amount": 50, "reason": "I have important information to share."}'


@pytest.fixture
def debate_message_response():
    """Sample JSON response for debate message."""
    return '{"message": "I think we should carefully consider all the evidence before voting."}'


@pytest.fixture
def agent_url():
    """Default agent URL for testing."""
    return "http://localhost:9999"
