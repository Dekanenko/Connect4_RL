import pytest
import numpy as np
from src.game_engine.connect4_engine import Connect4Engine

@pytest.fixture
def engine():
    """Returns a Connect4Engine instance."""
    return Connect4Engine()

def test_initial_state(engine: Connect4Engine):
    """Test the initial state of the game."""
    assert np.all(engine.get_board() == np.zeros((Connect4Engine.ROWS, Connect4Engine.COLS), dtype=np.int8))
    assert engine.current_player == Connect4Engine.PLAYER_1
    assert not engine.game_over
    assert engine.winner is None
    assert engine.moves_left == Connect4Engine.ROWS * Connect4Engine.COLS
    assert len(engine.get_valid_actions()) == Connect4Engine.COLS

def test_step_valid_move(engine: Connect4Engine):
    """Test a valid move."""
    valid, done, winner = engine.step(0)
    assert valid
    assert not done
    assert winner is None
    assert engine.get_board()[Connect4Engine.ROWS - 1, 0] == Connect4Engine.PLAYER_1
    assert engine.current_player == Connect4Engine.PLAYER_2
    assert engine.moves_left == Connect4Engine.ROWS * Connect4Engine.COLS - 1

def test_step_invalid_move_full_column(engine: Connect4Engine):
    """Test making a move in a full column."""
    for _ in range(Connect4Engine.ROWS):
        engine.step(0)
    
    valid, done, winner = engine.step(0)
    assert not valid
    assert not done
    assert winner is None

def test_step_game_over(engine: Connect4Engine):
    """Test making a move after the game is over."""
    engine.game_over = True
    engine.winner = Connect4Engine.PLAYER_1
    valid, done, winner = engine.step(0)
    assert not valid
    assert done
    assert winner == Connect4Engine.PLAYER_1

def test_horizontal_win(engine: Connect4Engine):
    """Test a horizontal win."""
    for i in range(3):
        engine.step(i)  # P1
        engine.step(i)  # P2
    valid, done, winner = engine.step(3) # P1 wins
    assert valid
    assert done
    assert winner == Connect4Engine.PLAYER_1

def test_vertical_win(engine: Connect4Engine):
    """Test a vertical win."""
    for i in range(3):
        engine.step(0)  # P1
        engine.step(1)  # P2
    valid, done, winner = engine.step(0) # P1 wins
    assert valid
    assert done
    assert winner == Connect4Engine.PLAYER_1

def test_diagonal_win_pos(engine: Connect4Engine):
    """Test a positive diagonal win (bottom-left to top-right)."""
    engine.step(0) # P1
    engine.step(1) # P2
    engine.step(1) # P1
    engine.step(2) # P2
    engine.step(2) # P1
    engine.step(3) # P2
    engine.step(2) # P1
    engine.step(3) # P2
    engine.step(3) # P1
    engine.step(0) # P2
    valid, done, winner = engine.step(3) # P1 wins
    assert valid
    assert done
    assert winner == Connect4Engine.PLAYER_1

def test_diagonal_win_neg(engine: Connect4Engine):
    """Test a negative diagonal win (top-left to bottom-right)."""
    engine.step(3) # P1
    engine.step(2) # P2
    engine.step(2) # P1
    engine.step(1) # P2
    engine.step(1) # P1
    engine.step(0) # P2
    engine.step(1) # P1
    engine.step(0) # P2
    engine.step(0) # P1
    engine.step(3) # P2
    valid, done, winner = engine.step(0) # P1 wins
    assert valid
    assert done
    assert winner == Connect4Engine.PLAYER_1
    
def test_draw(engine: Connect4Engine):
    """Test a draw game."""
    # Fill the board in a way that no one wins
    board = np.array([
        [0, 2, 1, 2, 1, 2, 1],
        [1, 1, 1, 2, 1, 2, 1],
        [2, 1, 2, 1, 2, 1, 2],
        [1, 2, 1, 2, 1, 2, 1],
        [1, 2, 1, 2, 2, 2, 1],
        [1, 1, 2, 1, 2, 1, 2]
    ])
    engine.board = board
    engine.moves_left = 1
    engine.current_player = Connect4Engine.PLAYER_1
    
    valid, done, winner = engine.step(0)
    assert valid
    assert done
    assert winner == Connect4Engine.DRAW

def test_get_valid_actions(engine: Connect4Engine):
    """Test get_valid_actions method."""
    assert np.array_equal(engine.get_valid_actions(), np.arange(Connect4Engine.COLS))
    for _ in range(Connect4Engine.ROWS):
        engine.step(0)
    assert np.array_equal(engine.get_valid_actions(), np.arange(1, Connect4Engine.COLS))
