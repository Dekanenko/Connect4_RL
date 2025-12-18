import torch
import numpy as np
import argparse
import mlflow
import mlflow.pytorch

from src.agent.dqn_agent import DQNAgent
from src.agent.engine_wrapper import Connect4Env
from src.game_engine.connect4_engine import Connect4Engine
from src.agent.rule_based_agent import RuleBasedAgent


def print_board(board: np.ndarray):
    """Prints the Connect4 board to the console."""
    rows, cols = board.shape
    header = " " + " ".join(str(i) for i in range(cols)) + " "
    print(header)
    print("-" * len(header))
    for r in range(rows):
        row_str = "|" + "|".join(
            "X" if cell == 1 else "O" if cell == 2 else " " for cell in board[r]
        ) + "|"
        print(row_str)
    print("-" * len(header))


def get_player_move(valid_actions: list[int]) -> int:
    """Prompts the human player for a move and validates it."""
    while True:
        try:
            move = int(input(f"Enter your move ({valid_actions}): "))
            if move in valid_actions:
                return move
            else:
                print("Invalid move. Please choose a valid column.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def play(run_id: str, auto_play: bool):
    """Main function to run the gameplay loop."""
    env = Connect4Env()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # First, create the agent structure. We will load the model into this structure.
    agent = DQNAgent(
        state_shape=env.state_shape,
        actions_num=env.actions_num,
        env=env,
        device=device,
    )

    # Load the trained model
    try:
        if run_id:
            model_uri = f"mlruns/1/models/{run_id}/artifacts"
            print(f"Loading model from MLflow run: {run_id}")
            loaded_model = mlflow.pytorch.load_model(model_uri, map_location=device)
            # CRITICAL: Assign the loaded model's state dict to our agent
            agent.model.load_state_dict(loaded_model.state_dict())
        else:
            # Fallback to local model if no run_id is provided
            model_path = "models/dqn_agent.pth"
            print(f"Loading model from local path: {model_path}")
            agent.model.load_state_dict(torch.load(model_path, map_location=device))

    except (mlflow.exceptions.MlflowException, FileNotFoundError) as e:
        print(f"Error loading model: {e}")
        print("Please ensure the run_id is correct or a local model exists.")
        return
    
    agent.model.eval()

    state_np = env.reset()
    done = False

    # Determine who is Player 1 and Player 2 for this game
    ai_player_id = np.random.choice([Connect4Engine.PLAYER_1, Connect4Engine.PLAYER_2])
    opponent_player_id = Connect4Engine.PLAYER_2 if ai_player_id == Connect4Engine.PLAYER_1 else Connect4Engine.PLAYER_1
    
    opponent_agent = None
    if auto_play:
        opponent_agent = RuleBasedAgent(env=env, player_id=opponent_player_id)
        print(f"AI is player {'X' if ai_player_id == 1 else 'O'}. Opponent is RuleBasedAgent.")
    else:
        print(f"You are player {'X' if opponent_player_id == 1 else 'O'}. AI is player {'X' if ai_player_id == 1 else 'O'}.")


    while not done:
        board = env.engine.get_board()
        print_board(board)

        current_player = env.engine.current_player
        valid_actions = env.engine.get_valid_actions()

        if current_player == ai_player_id:
            print("AI is thinking...")
            state = torch.tensor(state_np, dtype=torch.float32, device=device)
            action = agent.act(state, epsilon=0.0)  # Greedy action
        else:
            if auto_play:
                action = opponent_agent.act()
            else:
                action = get_player_move(valid_actions)
        
        state_np, _, done, _ = env.step(action)

    # Game over
    print_board(env.engine.get_board())
    winner = env.engine.winner
    if winner == Connect4Engine.DRAW:
        print("It's a draw!")
    elif winner == ai_player_id:
        print("The AI won!")
    else:
        if auto_play:
            print("The RuleBasedAgent won!")
        else:
            print("Congratulations! You won!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play against a trained DQN agent.")
    parser.add_argument(
        "--run_id", type=str, default=None, help="MLflow run ID of the model to load."
    )
    parser.add_argument(
        '--auto_play', action='store_true', default=False, help='Let the RuleBasedAgent play against the AI.'
    )
    args = parser.parse_args()
    play(args.run_id, args.auto_play)
