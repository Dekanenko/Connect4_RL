import argparse
import mlflow
from src.training.trainer import Trainer


def main():
    parser = argparse.ArgumentParser(description="Train a DQN agent for Connect4.")
    parser.add_argument(
        "--episodes", type=int, default=5000, help="Number of episodes to train for."
    )
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate.")
    parser.add_argument(
        "--eval_freq", type=int, default=1000, help="Frequency of evaluation."
    )

    args = parser.parse_args()

    # Set the experiment name for MLflow
    mlflow.set_experiment("Connect4 DQN Training")

    with mlflow.start_run():
        trainer = Trainer(
            learning_rate=0.00078,
            learning_rate_decay=0.99,
            gamma=0.9514,
            epsilon_decay=0.9998,
            epsilon_min=0.15,
            num_episodes=50000,
            eval_freq=args.eval_freq,
            store_best_model=True,
        )
        trainer.train()


if __name__ == "__main__":
    main()
