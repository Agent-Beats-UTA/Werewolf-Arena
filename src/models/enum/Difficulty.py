from enum import Enum


class Difficulty(Enum):
    """Game difficulty levels affecting AI participant strength."""
    EASY = "easy"
    HARD = "hard"
    
    def get_model(self) -> str:
        """Return the LLM model for this difficulty level."""
        if self == Difficulty.EASY:
            return "gemini-1.5-flash"
        elif self == Difficulty.HARD:
            return "gemini-2.0-flash"
        else:
            return "gemini-2.0-flash"