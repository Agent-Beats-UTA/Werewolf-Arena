# Green Agent - Werewolf Game Orchestrator

An Agent-to-Agent (A2A) evaluation server that orchestrates and manages Werewolf game sessions between multiple AI agents.

## Overview

The Green Agent is responsible for running complete Werewolf game evaluations. It manages game state, coordinates communication between agent participants (villagers, werewolves, seer), executes game phases, and tracks outcomes.

## Architecture

### Core Components

- **A2A Server** (`__main__.py`): HTTP server exposing agent capabilities via A2A protocol on port 9999
- **Game Controller** (`src/game/Game.py`): Main game loop and phase orchestration
- **Green Agent** (`src/a2a/agent.py`): Primary agent logic that processes evaluation requests
- **Messenger** (`src/a2a/messenger.py`): Handles agent-to-agent communication
- **Game State** (`src/game/GameData.py`): Maintains all game state and participant data

### Game Phases

The game executes in the following sequential phases each round:

1. **Night** (`src/phases/night.py`)
   - Werewolf selects a player to eliminate
   - Seer investigates one player to learn their role

2. **Bidding** (`src/phases/bidding.py`)
   - Players bid for speaking priority in discussion

3. **Discussion** (`src/phases/discussion.py`)
   - Players communicate and share information based on bidding order

4. **Voting** (`src/phases/voting.py`)
   - Players vote to eliminate a suspected werewolf

5. **Round End** (`src/phases/round_end.py`)
   - Process eliminations and check win conditions

6. **Game End** (`src/phases/game_end.py`)
   - Finalize results and analytics

### Models

- **Participant** (`src/models/Participant.py`): Represents an agent player
- **Event** (`src/models/Event.py`): Game event logging
- **Vote** (`src/models/Vote.py`): Voting data structure
- **Elimination** (`src/models/Elimination.py`): Elimination tracking
- **Enums** (`src/models/enum/`): Phase, Role, Status, EventType definitions

## Running the Server

```bash
# Using Python
python -m greenAgent

# Using Docker
docker build -t green-agent .
docker run -p 9999:9999 green-agent
```

The server will start on `http://0.0.0.0:9999` and expose the A2A agent card.

## Game Flow

1. Receive `EvalRequest` with participant agent URLs
2. Assign roles randomly to participants (Villagers, Werewolf, Seer)
3. Execute game phases in sequence until:
   - Werewolf is eliminated (villagers win)
   - Werewolves equal or outnumber villagers (werewolves win)
4. Return evaluation results and analytics

## Dependencies

- **a2a-sdk**: Agent-to-Agent protocol implementation with HTTP server support
- **agentbeats**: Agent monitoring and telemetry
- **uvicorn**: ASGI server
- **uuid**: Unique identifier generation

See `pyproject.toml` for complete dependency list.

## API

The Green Agent accepts `EvalRequest` messages via A2A protocol containing:
- `participants`: Map of role names to agent URLs
- `config`: Evaluation configuration parameters

## Development

The agent uses Python 3.13+ and the A2A SDK for agent communication. All game logic is event-driven and logged for evaluation purposes.
