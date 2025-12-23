import uuid
import torch
import time
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
from random import choice, random

from connect4.game.engine_wrapper import Connect4Env
from connect4.api.schemas import GameStateResponse, MoveRequest, HealthResponse
from connect4.game.engine import Connect4Engine

router = APIRouter()

# --- In-Memory Session Storage with TTL ---
SESSION_TTL_SECONDS = 3600  # 1 hour
game_sessions: Dict[str, Dict[str, Any]] = {}


def clean_stale_sessions():
    """
    A dependency that cleans up old game sessions.
    This runs before creating a new game to prevent the session dictionary
    from growing indefinitely.
    """
    current_time = time.time()
    stale_sessions = [
        session_id
        for session_id, data in game_sessions.items()
        if current_time - data["last_accessed"] > SESSION_TTL_SECONDS
    ]
    for session_id in stale_sessions:
        del game_sessions[session_id]


@router.get("/health", response_model=HealthResponse, tags=["Game"])
async def health_check():
    """Checks if the API is running."""
    return HealthResponse()


@router.post("/game/init", response_model=GameStateResponse, tags=["Game"])
async def initialize_game(request: Request, _: None = Depends(clean_stale_sessions)):
    """
    Initializes a new game session.
    - Cleans up any stale sessions.
    - Randomly decides if the AI or the human goes first.
    - If the AI is first, it makes its opening move.
    """
    session_id = str(uuid.uuid4())
    env = Connect4Env()
    
    ai_player = choice([Connect4Engine.PLAYER_1, Connect4Engine.PLAYER_2])
    human_player = Connect4Engine.PLAYER_2 if ai_player == Connect4Engine.PLAYER_1 else Connect4Engine.PLAYER_1
    
    print(f"AI player: {ai_player}, Human player: {human_player}")
    print(f"Current player: {env.engine.current_player}")

    # If AI is Player 1, it needs to make the first move.
    if ai_player == env.engine.current_player:
        print(f"AI is current player: {env.engine.current_player}")
        agent = request.app.state.agent
        if random() < 0.5: # 50% chance to use the agent, 50% chance to use a random move
            print("Using agent")
            state_np = env._get_state()
            state = torch.tensor(state_np, dtype=torch.float32, device=agent.device)
            action = agent.act(state, epsilon=0.0)
        else:
            print("Using random move")
            action = choice(env.engine.get_valid_actions())
        
        print(f"Action: {action}")
        
        env.step(action)
    
    game_sessions[session_id] = {
        "env": env,
        "last_accessed": time.time(),
        "ai_player": ai_player,
        "human_player": human_player,
    }
    
    return GameStateResponse(
        session_id=session_id,
        board=env.engine.get_board().tolist(),
        ai_player=ai_player,
        human_player=human_player,
        current_player=env.engine.current_player,
    )


@router.post("/game/move", response_model=GameStateResponse, tags=["Game"])
async def make_move(request: Request, move: MoveRequest):
    """
    Processes a player's move and gets the AI's response.
    """
    session_data = game_sessions.get(move.session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Game session not found.")
    
    env = session_data["env"]
    session_data["last_accessed"] = time.time() # Update timestamp on activity

    agent = request.app.state.agent
    
    # --- Human's Turn ---
    if env.engine.current_player != session_data["human_player"]:
        raise HTTPException(status_code=400, detail="It's not your turn.")
    
    if move.column not in env.engine.get_valid_actions():
        raise HTTPException(status_code=400, detail="Invalid move.")

    state_np, _, done, _ = env.step(move.column)
    
    # --- AI's Turn (if the game is not over) ---
    if not done:
        state = torch.tensor(state_np, dtype=torch.float32, device=agent.device)
        action = agent.act(state, epsilon=0.0)
        env.step(action)
    
    return GameStateResponse(
        session_id=move.session_id,
        board=env.engine.get_board().tolist(),
        ai_player=session_data["ai_player"],
        human_player=session_data["human_player"],
        current_player=env.engine.current_player,
        game_over=env.engine.game_over,
        winner=env.engine.winner,
    )