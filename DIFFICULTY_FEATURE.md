# Difficulty Setting Feature

## Overview

The Green Agent now supports **difficulty levels** for game evaluations. This allows evaluations to be conducted with simulated participants using different LLM models, reflecting different opponent strengths.

## Difficulty Levels

### Easy Mode
- **Model**: `gemini-1.5-flash`
- **Use Case**: Testing against a smaller, faster model
- **Impact**: Simulated participants will use a lighter-weight model, making the game potentially easier for the evaluated agent
- **Leaderboard**: Easy mode scores are tracked separately

### Hard Mode
- **Model**: `gemini-2.0-flash`
- **Use Case**: Testing against a larger, more capable model (default)
- **Impact**: Simulated participants will use the latest advanced model, providing a stronger challenge
- **Leaderboard**: Hard mode scores are tracked separately

## Usage

### In an EvalRequest

Send difficulty as part of the evaluation request JSON:

```json
{
  "participants": {
    "agent1": "http://localhost:8001"
  },
  "difficulty": "easy"
}
```

**Valid values**: `"easy"` or `"hard"`
**Default**: `"hard"` (if not specified)

### Example Requests

```bash
# Hard mode (default)
curl -X POST http://localhost:9009/message \
  -H "Content-Type: application/json" \
  -d '{
    "participants": {
      "agent1": "http://localhost:8001"
    },
    "difficulty": "hard"
  }'

# Easy mode
curl -X POST http://localhost:9009/message \
  -H "Content-Type: application/json" \
  -d '{
    "participants": {
      "agent1": "http://localhost:8001"
    },
    "difficulty": "easy"
  }'
```

## Implementation Details

### Files Modified/Created

1. **`src/models/enum/Difficulty.py`** (New)
   - Defines the `Difficulty` enum with `EASY` and `HARD` values
   - `get_model()` method returns the appropriate LLM model name

2. **`src/models/EvalRequest.py`** (Modified)
   - Added `difficulty` field with default value of `Difficulty.HARD`
   - Accepts string values ("easy" or "hard") via Pydantic

3. **`src/services/llm.py`** (Modified)
   - Added `difficulty` parameter to LLM constructor
   - Model selection is now based on the provided difficulty level
   - Defaults to `Difficulty.HARD`

4. **`src/models/Participant.py`** (Modified)
   - Added `difficulty` field to the Participant model
   - Participants are created with the appropriate difficulty setting

5. **`src/a2a/agent.py`** (Modified)
   - `run()` method extracts difficulty from the EvalRequest
   - Passes difficulty to `run_single_game()` and `init_game()`
   - `init_game()` creates LLM participants with the correct difficulty
   - Analytics now include difficulty level in results

6. **`tests/conftest.py`** (Modified)
   - Updated fixtures to support difficulty parameter
   - `create_mock_participant()` now accepts difficulty argument

7. **`tests/test_difficulty.py`** (New)
   - Comprehensive test suite for difficulty feature
   - Tests for enum, LLM integration, Participant integration, and EvalRequest parsing

## Analytics and Leaderboard Integration

### Difficulty in Results

The aggregate analytics now include the difficulty level:

```json
{
  "total_games": 8,
  "games_per_role": 2,
  "difficulty": "easy",
  "overall_win_rate": 0.625,
  "overall_total_score": 450,
  "by_role": {
    "VILLAGER": {
      "games_played": 2,
      "win_rate": 0.75,
      ...
    }
    ...
  }
}
```

### Leaderboard Considerations

When integrating with a leaderboard system:
- Store difficulty level with each evaluation result
- Display separate leaderboards or rankings for each difficulty level
- Consider weighting hard mode scores higher (e.g., 1.5x multiplier)
- Show both difficulty levels in player profiles

Example leaderboard structure:
```
Player A - Hard Mode: 3500 points (8 games)
Player A - Easy Mode: 4200 points (8 games)
```

## Model Details

### Gemini 1.5 Flash (Easy)
- **Speed**: Fast, optimized for quick responses
- **Size**: Smaller model, fewer parameters
- **Cost**: Lower API cost
- **Use**: Quick evaluations, baseline performance

### Gemini 2.0 Flash (Hard)
- **Speed**: Fast with improved reasoning
- **Size**: Latest generation model with more capabilities
- **Cost**: Higher API cost
- **Use**: Comprehensive evaluations, advanced opponent

## Future Extensions

Possible future enhancements:
- Add more difficulty levels (e.g., `MEDIUM`, `EXPERT`)
- Add model selection via configuration file
- Support custom model selection per role
- Add difficulty multipliers for scoring
- Support difficulty-specific game rules

## Testing

Run the difficulty tests:

```bash
# Run all difficulty tests
pytest tests/test_difficulty.py -v

# Run specific difficulty test
pytest tests/test_difficulty.py::TestDifficultyEnum -v

# Run with coverage
pytest tests/test_difficulty.py --cov=src --cov-report=html
```

## Example Full Workflow

1. **Request evaluation (easy mode)**:
   ```json
   {
     "participants": {"agent1": "http://localhost:8001"},
     "difficulty": "easy"
   }
   ```

2. **GreenAgent processes the request**:
   - Parses EvalRequest with `difficulty: "easy"`
   - Creates game with easy-difficulty LLM participants
   - Simulated participants use `gemini-1.5-flash` model

3. **Games run** with 8 total games (2 per role):
   - Agent plays as Villager, Werewolf, Seer, and Doctor
   - Against easy-mode LLM opponents
   - Against 6-player games (standard composition)

4. **Results returned** with difficulty metadata:
   - Individual game analytics
   - Aggregate statistics
   - Win rates and scores by role
   - **difficulty: "easy"** marked in all results

5. **Leaderboard integration**:
   - Results stored with difficulty level
   - Separate leaderboard entries for easy and hard mode
   - Comparison possible between difficulty levels