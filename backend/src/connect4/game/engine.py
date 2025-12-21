import numpy as np
from typing import Optional, Tuple


class Connect4Engine:
    ROWS = 6
    COLS = 7
    EMPTY = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    DRAW = 3

    def __init__(self):
        self.reset()

    # ------------------------
    # Core API
    # ------------------------

    def reset(self) -> None:
        """Reset the game to the initial state."""
        self.board = np.zeros((self.ROWS, self.COLS), dtype=np.int8)
        self.current_player = self.PLAYER_1
        self.game_over = False
        self.winner: Optional[int] = None
        self.moves_left = self.ROWS * self.COLS

    def step(self, action: int) -> Tuple[bool, bool, Optional[int]]:
        """
        Apply a move for the current player.

        Args:
            action (int): column index [0..6]

        Returns:
            valid (bool): whether the move was applied
            done (bool): whether the game ended
            winner (Optional[int]): PLAYER_1, PLAYER_2, DRAW, or None
        """
        if self.game_over:
            return False, True, self.winner

        if action not in self.get_valid_actions():
            return False, False, None

        row = self._get_next_empty_row(action)
        player = self.current_player

        self.board[row, action] = player
        self.moves_left -= 1

        result = self._check_winner(player)

        if result is not None:
            self.game_over = True
            self.winner = result
        else:
            self.current_player = self._switch_player(player)

        return True, self.game_over, self.winner

    # ------------------------
    # State helpers
    # ------------------------

    def get_valid_actions(self) -> np.ndarray:
        """Return columns where a move is possible."""
        return np.where(self.board[0] == self.EMPTY)[0]
    
    def get_valid_actions_from_state(self, board: np.ndarray) -> np.ndarray:
        """Return columns where a move is possible for the given board state."""
        return np.where(board[0] == self.EMPTY)[0]


    def get_board(self) -> np.ndarray:
        """Return a copy of the current board."""
        return self.board.copy()

    # ------------------------
    # Internal helpers
    # ------------------------

    def _switch_player(self, player: int) -> int:
        return self.PLAYER_2 if player == self.PLAYER_1 else self.PLAYER_1

    def _get_next_empty_row(self, col: int) -> int:
        if not 0 <= col < self.COLS:
            raise ValueError(f"Column {col} is out of bounds.")
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row, col] == self.EMPTY:
                return row
        raise ValueError("Column is full")

    def check_win_on_board(self, board: np.ndarray, player: int) -> bool:
        """Checks if a player has won on a given board state."""
        # Horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if np.all(board[row, col:col + 4] == player):
                    return True

        # Vertical
        for row in range(self.ROWS - 3):
            for col in range(self.COLS):
                if np.all(board[row:row + 4, col] == player):
                    return True

        # Diagonal (top-left → bottom-right)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if all(board[row + i, col + i] == player for i in range(4)):
                    return True

        # Diagonal (bottom-left → top-right)
        for row in range(3, self.ROWS):
            for col in range(self.COLS - 3):
                if all(board[row - i, col + i] == player for i in range(4)):
                    return True
        
        return False

    def _check_winner(self, player: int) -> Optional[int]:
        if self.check_win_on_board(self.board, player):
            return player

        # Draw
        if self.moves_left == 0:
            return self.DRAW

        return None
