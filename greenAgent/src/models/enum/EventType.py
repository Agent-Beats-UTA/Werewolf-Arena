from enum import Enum, auto

class EventType(Enum):
    VILLAGE_ELIMINATION = auto()
    WEREWOLF_ELIMINATION = auto()
    SEER_INVESTIGATION = auto()
    VOTE = auto()
    DEBATE = auto()
    NIGHT_END = auto()
    ROUND_END = auto()
    GAME_END = auto()
    SPEAKING_ORDER_SET = auto()
    