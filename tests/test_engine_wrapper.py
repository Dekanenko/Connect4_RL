import pytest
import numpy as np
from src.agent.engine_wrapper import Connect4Env
from src.game_engine.connect4_engine import Connect4Engine

@pytest.fixture
def env():
    """Returns a Connect4Env instance."""
    return Connect4Env()

def test_initial_state(env: Connect4Env):
    """Test the initial state of the environment."""
    state = env.reset()
    assert state.shape == (2, Connect4Engine.ROWS, Connect4Engine.COLS)
    assert np.all(state == np.zeros((2, Connect4Engine.ROWS, Connect4Engine.COLS)))
    assert env.engine.current_player == Connect4Engine.PLAYER_1

def test_step(env: Connect4Env):
    """Test a single step in the environment."""
    initial_state = env.reset()
    action = 0
    next_state, reward, done, _ = env.step(action)

    assert next_state.shape == (2, Connect4Engine.ROWS, Connect4Engine.COLS)
    assert reward == 0.0
    assert not done

    # After P1 moves, it's P2's turn. The state should reflect P2's perspective.
    # P1's piece at the bottom of column 0 is now the opponent's piece.
    expected_opp_board = np.zeros((Connect4Engine.ROWS, Connect4Engine.COLS))
    expected_opp_board[Connect4Engine.ROWS - 1, 0] = 1.0
    
    assert np.all(next_state[0] == np.zeros((Connect4Engine.ROWS, Connect4Engine.COLS))) # P2's board is empty
    assert np.all(next_state[1] == expected_opp_board) # P1's piece is on the opponent board

def test_win_reward(env: Connect4Env):
    """Test the reward for a winning move."""
    env.reset()
    # P1 moves
    env.step(0)
    # P2 moves
    env.step(0)
    # P1 moves
    env.step(1)
    # P2 moves
    env.step(1)
    # P1 moves
    env.step(2)
    # P2 moves
    env.step(2)
    # P1 makes winning move
    _, reward, done, _ = env.step(3)

    assert done
    assert reward == 1.0

def test_loss_reward(env: Connect4Env):
    """Test the reward for a losing move."""
    env.reset()
    # P1 moves
    env.step(0)
    # P2 moves
    env.step(0)
    # P1 moves
    env.step(0)
    # P2 moves
    env.step(0)
    # P1 moves
    env.step(0)
    # P2 moves
    env.step(0)
    _, reward, done, _ = env.step(0) # P1 makes incorrect move

    assert done
    assert reward == -2.0 # From P1's perspective after P2 wins

def test_draw_reward(env: Connect4Env):
    """Test the reward for a draw."""
    env.reset()
    
    # Manually set up a board state that will result in a draw
    board = np.array([
        [0, 2, 1, 2, 1, 2, 1],
        [1, 1, 1, 2, 1, 2, 1],
        [2, 1, 2, 1, 2, 1, 2],
        [1, 2, 1, 2, 1, 2, 1],
        [1, 2, 1, 2, 2, 2, 1],
        [1, 1, 2, 1, 2, 1, 2]
    ])
    
    env.engine.board = board
    env.engine.moves_left = 1
    env.engine.current_player = Connect4Engine.PLAYER_1
    
    _, reward, done, _ = env.step(0)
    
    assert done
    assert reward == 0.0

def test_get_state(env: Connect4Env):
    """Test the _get_state method."""
    env.reset()
    env.step(0) # P1 moves in column 0
    state = env._get_state()

    # It's now player 2's turn
    assert env.engine.current_player == Connect4Engine.PLAYER_2
    
    # The state should be from player 2's perspective
    # Player 2's board should be empty
    assert np.all(state[0] == 0)
    # Player 1's move should be on the opponent's board
    assert state[1, Connect4Engine.ROWS - 1, 0] == 1.0
