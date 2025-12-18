import torch
import numpy as np
import os
import random
from tqdm import tqdm
import mlflow
import mlflow.pytorch

from src.agent.dqn_agent import DQNAgent
from src.agent.rule_based_agent import RuleBasedAgent
from src.agent.engine_wrapper import Connect4Env
from src.agent.buffer import ReplayBuffer
from src.game_engine.connect4_engine import Connect4Engine


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

        # Set the seed for reproducibility
        set_seed(self.params["seed"])

        # Setup
        self.env = Connect4Env()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.agent = DQNAgent(
            state_shape=self.env.state_shape,
            actions_num=self.env.actions_num,
            env=self.env,
            device=self.device,
            learning_rate=self.params["learning_rate"],
            gamma=self.params["gamma"],
        )
        self.buffer = ReplayBuffer(capacity=self.params["buffer_size"])

    def train(self) -> float:
        mlflow.log_params(self.params)
        global_step = 0
        final_eval_metrics = {}

        best_win_rate = 0.5
        best_episode = 0

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
                renamed_metrics = {f"eval_{k}": v for k, v in eval_metrics.items()}
                mlflow.log_metrics(renamed_metrics, step=episode)

                print(f"--- Evaluation at Episode {episode} ---")
                print(f"Win Rate vs Rule-Based: {eval_metrics['win_rate']:.2f}")
                print(f"Draw Rate vs Rule-Based: {eval_metrics['draw_rate']:.2f}")
                print(f"Loss Rate vs Rule-Based: {eval_metrics['loss_rate']:.2f}")
                print("------------------------------------")

                if self.params["store_best_model"] and eval_metrics["win_rate"] > best_win_rate:
                    best_win_rate = eval_metrics["win_rate"]
                    best_episode = episode
                    self.save_model()
            
            if episode % 1000 == 0:
                self.params["learning_rate"] = max(self.params["learning_rate"] * self.params["learning_rate_decay"], 1e-5)
                self.agent.optimizer.param_groups[0]["lr"] = self.params["learning_rate"]

        # self.save_model()
        print(f"Best Win Rate: {best_win_rate:.2f} at Episode {best_episode}")
        return final_eval_metrics.get("win_rate", 0.0)

    def evaluate(self) -> dict:
        self.agent.model.eval()
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
                    action = self.agent.act(state, epsilon=0.0)
                else:
                    action = rule_based_agent.act()
                state_np, _, done, _ = self.env.step(action)

            winner = self.env.engine.winner
            if winner == agent_player_id: wins += 1
            elif winner == Connect4Engine.DRAW: draws += 1
            else: losses += 1

        self.agent.model.train()
        total_games = self.params["num_eval_games"]
        return {
            "win_rate": wins / total_games,
            "draw_rate": draws / total_games,
            "loss_rate": losses / total_games,
        }

    def save_model(self):
        os.makedirs(self.save_dir, exist_ok=True)
        save_path = os.path.join(self.save_dir, "dqn_agent.pth")
        torch.save(self.agent.model.state_dict(), save_path)
        print(f"Model saved to {save_path}")

        mlflow.pytorch.log_model(self.agent.model, "model")
        print("Model also logged as an MLflow artifact.")
