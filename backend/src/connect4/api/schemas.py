from pydantic import BaseModel, Field
from typing import List, Optional

# --- Request Models ---

class MoveRequest(BaseModel):
    session_id: str = Field(..., description="The unique ID for the current game session.")
    column: int = Field(..., ge=0, le=6, description="The column where the player wants to move.")

# --- Response Models ---

class GameStateResponse(BaseModel):
    session_id: str = Field(..., description="The unique ID for the current game session.")
    board: List[List[int]] = Field(..., description="The current state of the game board.")
    ai_player: int = Field(..., description="Which player the AI is (1 or 2).")
    human_player: int = Field(..., description="Which player the human is (1 or 2).")
    current_player: int = Field(..., description="The player whose turn it is.")
    game_over: bool = Field(False, description="Whether the game has ended.")
    winner: Optional[int] = Field(None, description="The winner of the game, if it has ended (1, 2, or 3 for a draw).")

class HealthResponse(BaseModel):
    status: str = "ok"

