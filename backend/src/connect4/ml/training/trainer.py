import torch
import numpy as np
import os
import random
from tqdm import tqdm
import mlflow
import mlflow.pytorch

from connect4.ml.agent.dqn_agent import DQNAgent
from connect4.ml.agent.rule_based_agent import RuleBasedAgent
from connect4.game.engine_wrapper import Connect4Env
from connect4.ml.training.replay_buffer import ReplayBuffer
from connect4.game.engine import Connect4Engine


def set_seed(seed: int):
    """Sets the random seed for reproducibility across different libraries."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # When running on the CuDNN backend, two further options must be set
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"Random seed set to {seed}")


class Trainer:
    def __init__(
        self,
        learning_rate=1e-4,
        learning_rate_decay=0.999,
        gamma=0.99,
        buffer_size=500_000,
        num_episodes=30000,
        batch_size=32,
        warmup_steps=1000,
        target_update_freq=1000,
        eval_freq=1000,
        num_eval_games=100,
        epsilon_start=1.0,
        epsilon_min=0.1,
        epsilon_decay=0.9993,
        save_dir="models",
        seed=42,
        store_best_model=False,
    ):
        # Hyperparameters
        self.params = {
            "learning_rate": learning_rate,
            "learning_rate_decay": learning_rate_decay,
            "gamma": gamma,
            "buffer_size": buffer_size,
            "num_episodes": num_episodes,
            "batch_size": batch_size,
            "warmup_steps": warmup_steps,
            "target_update_freq": target_update_freq,
            "eval_freq": eval_freq,
            "num_eval_games": num_eval_games,
            "epsilon_start": epsilon_start,
            "epsilon_min": epsilon_min,
            "epsilon_decay": epsilon_decay,
            "seed": seed,
            "store_best_model": store_best_model,
        }
        self.epsilon = epsilon_start
        self.save_dir = save_dir
        self.best_model_save_path = os.path.join(self.save_dir, "dqn_agent.pth")
        self.best_win_rate = 0.5  # Initial threshold to save a model

        # Set the seed for reproducibility
        set_seed(self.params["seed"])

        # Setup
        self.env = Connect4Env()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.agent = DQNAgent(
            state_shape=self.env.state_shape,
            actions_num=self.env.actions_num,
            device=self.device,
            learning_rate=self.params["learning_rate"],
            gamma=self.params["gamma"],
        )
        self.buffer = ReplayBuffer(capacity=self.params["buffer_size"])

    def train(self) -> float:
        mlflow.log_params(self.params)
        global_step = 0
        final_eval_metrics = {}

        for episode in range(1, self.params["num_episodes"] + 1):
            state_np = self.env.reset()
            state = torch.tensor(state_np, dtype=torch.float32, device=self.device)
            done = False
            episode_reward = 0.0

            while not done:
                global_step += 1
                action = self.agent.act(state, self.epsilon)
                next_state_np, reward, done, _ = self.env.step(action)
                next_state = torch.tensor(
                    next_state_np, dtype=torch.float32, device=self.device
                )

                self.buffer.push(state, action, reward, next_state, done)
                state = next_state
                episode_reward += reward

                if len(self.buffer) >= self.params["warmup_steps"]:
                    batch = self.buffer.sample(self.params["batch_size"])
                    self.agent.train_step(batch)

                    if global_step % self.params["target_update_freq"] == 0:
                        self.agent.update_target()

            self.epsilon = max(
                self.params["epsilon_min"], self.epsilon * self.params["epsilon_decay"]
            )
            
            mlflow.log_metric("episode_reward", episode_reward, step=episode)
            mlflow.log_metric("epsilon", self.epsilon, step=episode)

            if episode % 100 == 0:
                print(
                    f"Episode {episode:5d} | "
                    f"Reward: {episode_reward:6.2f} | "
                    f"Epsilon: {self.epsilon:.3f} | "
                    f"Learning Rate: {self.params['learning_rate']:.6f}"
                )

            if episode % self.params["eval_freq"] == 0:
                eval_metrics = self.evaluate()
                final_eval_metrics = eval_metrics
                mlflow.log_metrics(eval_metrics, step=episode)

                print(f"--- Evaluation at Episode {episode} ---")
                print(f"Win Rate vs Rule-Based: {eval_metrics['win_rate_vs_rules']:.2f}")
                if "win_rate_vs_best" in eval_metrics:
                    print(f"Win Rate vs Previous Best: {eval_metrics['win_rate_vs_best']:.2f}")
                print("------------------------------------")

                if self.params["store_best_model"]:
                    win_rate_vs_rules = eval_metrics["win_rate_vs_rules"]
                    new_best_found = False

                    # Case 1: High-performance regime (must beat previous best)
                    if "win_rate_vs_best" in eval_metrics:
                        win_rate_vs_best = eval_metrics["win_rate_vs_best"]
                        if win_rate_vs_rules >= self.best_win_rate and win_rate_vs_best > 0.50:
                            new_best_found = True
                    # Case 2: Standard improvement (before vs-best evaluation is triggered)
                    else:
                        if win_rate_vs_rules > self.best_win_rate:
                            new_best_found = True
                    
                    if new_best_found:
                        self.best_win_rate = win_rate_vs_rules
                        print(f"New best model found at episode {episode} with win rate {self.best_win_rate:.2f}. Saving model.")
                        self.save_model()
            
            if episode % 1000 == 0:
                self.params["learning_rate"] = max(self.params["learning_rate"] * self.params["learning_rate_decay"], 1e-5)
                self.agent.optimizer.param_groups[0]["lr"] = self.params["learning_rate"]

        print(f"Training finished. Best win rate vs rules: {self.best_win_rate:.2f}")
        return final_eval_metrics.get("win_rate_vs_rules", 0.0)

    def _run_evaluation_games(self, opponent, description: str) -> dict:
        """Helper function to run evaluation games against a given opponent."""
        self.agent.model.eval()
        wins, draws, losses = 0, 0, 0
        is_opponent_dqn = isinstance(opponent, DQNAgent)

        if is_opponent_dqn:
            opponent.model.eval()

        for _ in tqdm(range(self.params["num_eval_games"]), desc=description):
            state_np = self.env.reset()
            done = False
            agent_player_id = np.random.choice([Connect4Engine.PLAYER_1, Connect4Engine.PLAYER_2])

            # Set the rule-based agent's player ID for the current game
            if not is_opponent_dqn:
                opponent.player_id = 3 - agent_player_id
                opponent.opponent_id = agent_player_id

            while not done:
                current_player = self.env.engine.current_player
                state = torch.tensor(state_np, dtype=torch.float32, device=self.device)

                if current_player == agent_player_id:
                    action = self.agent.act(state, epsilon=0.0)
                else:  # Opponent's turn
                    if is_opponent_dqn:
                        action = opponent.act(state, epsilon=0.0)
                    else: # Assumes RuleBasedAgent
                        action = opponent.act()
                
                state_np, _, done, _ = self.env.step(action)

            winner = self.env.engine.winner
            if winner == agent_player_id: wins += 1
            elif winner == Connect4Engine.DRAW: draws += 1
            else: losses += 1

        self.agent.model.train()
        total_games = self.params["num_eval_games"]
        return {
            "wins": wins / total_games,
            "draws": draws / total_games,
            "losses": losses / total_games,
        }

    def evaluate(self) -> dict:
        """
        Orchestrates the evaluation process against the rule-based agent and,
        if applicable, against the previous best model.
        """
        # --- Stage 1: Evaluate against Rule-Based Agent ---
        # The gameplay logic here remains the same as your original implementation.
        rule_based_agent = RuleBasedAgent(env=self.env, player_id=-1)  # ID is set in helper
        metrics_vs_rules = self._run_evaluation_games(
            opponent=rule_based_agent, description="Evaluating vs Rules"
        )
        
        metrics = {
            "win_rate_vs_rules": metrics_vs_rules["wins"],
            "draw_rate_vs_rules": metrics_vs_rules["draws"],
            "loss_rate_vs_rules": metrics_vs_rules["losses"],
        }

        # --- Stage 2: Conditionally Evaluate against Previous Best ---
        if metrics["win_rate_vs_rules"] >= 0.70:
            if not os.path.exists(self.best_model_save_path):
                print("\nWin rate >= 70% but no previous best model found to compare against. Skipping.")
            else:
                print("\nWin rate >= 70%. Evaluating against previous best model.")
                previous_best_agent = DQNAgent(
                    state_shape=self.env.state_shape,
                    actions_num=self.env.actions_num,
                    device=self.device,
                )
                previous_best_agent.model.load_state_dict(
                    torch.load(self.best_model_save_path, map_location=self.device)
                )

                self.check_previous_best_model(previous_best_agent)

                metrics_vs_best = self._run_evaluation_games(
                    opponent=previous_best_agent, description="Evaluating vs Best"
                )
                metrics["win_rate_vs_best"] = metrics_vs_best["wins"]
                metrics["draw_rate_vs_best"] = metrics_vs_best["draws"]
                metrics["loss_rate_vs_best"] = metrics_vs_best["losses"]

        return metrics
    
    def check_previous_best_model(self, previous_best_agent) -> dict:
        previous_best_agent.model.eval()
        wins, draws, losses = 0, 0, 0

        for _ in tqdm(range(self.params["num_eval_games"]), desc="Evaluating"):
            state_np = self.env.reset()
            done = False

            agent_player_id = np.random.choice([Connect4Engine.PLAYER_1, Connect4Engine.PLAYER_2])
            opponent_player_id = (
                Connect4Engine.PLAYER_2 if agent_player_id == Connect4Engine.PLAYER_1 else Connect4Engine.PLAYER_1
            )
            rule_based_agent = RuleBasedAgent(env=self.env, player_id=opponent_player_id)

            while not done:
                current_player = self.env.engine.current_player
                if current_player == agent_player_id:
                    state = torch.tensor(state_np, dtype=torch.float32, device=self.device)
                    action = previous_best_agent.act(state, epsilon=0.0)
                else:
                    action = rule_based_agent.act()
                state_np, _, done, _ = self.env.step(action)

            winner = self.env.engine.winner
            if winner == agent_player_id: wins += 1
            elif winner == Connect4Engine.DRAW: draws += 1
            else: losses += 1

        total_games = self.params["num_eval_games"]
        metrics = {
            "win_rate": wins / total_games,
            "draw_rate": draws / total_games,
            "loss_rate": losses / total_games,
        }
        print(f"Win rate (rule based agent vs previous best agent): {metrics['win_rate']:.2f}")

    def save_model(self):
        os.makedirs(self.save_dir, exist_ok=True)
        torch.save(self.agent.model.state_dict(), self.best_model_save_path)
        print(f"Model saved to {self.best_model_save_path}")

        mlflow.pytorch.log_model(self.agent.model, "model")
        print("Model also logged as an MLflow artifact.")
