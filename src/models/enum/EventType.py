from enum import Enum, auto

class EventType(Enum):
    VILLAGE_ELIMINATION = auto()
    WEREWOLF_ELIMINATION = auto()
    WEREWOLF_ELIMINATION_FAILURE = auto()
    SEER_INVESTIGATION = auto()
    DOCTOR_SAVE = auto()
    VOTE = auto()
    BID_PLACED = auto()
    DEBATE = auto()
    NIGHT_END = auto()
    ROUND_END = auto()
    GAME_END = auto()
    SPEAKING_ORDER_SET = auto()
    