from enum import Enum, auto

class EliminationType(Enum):
    NIGHT_KILL = auto()
    VOTED_OUT = auto()
    
class EliminationStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()