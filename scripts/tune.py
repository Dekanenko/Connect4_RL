import argparse
import optuna
import mlflow
import sys
import os

# --- Add the backend source to the Python path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_src_path = os.path.join(project_root, 'backend', 'src')
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)
# ---------------------------------------------

from connect4.ml.training.trainer import Trainer


def objective(trial: optuna.Trial) -> float:
    """
    The objective function to be maximized by Optuna.
    A single trial consists of training a model with a set of hyperparameters.
    """
    # MLflow will create a new run for each trial
    with mlflow.start_run(nested=True):
        # Define the hyperparameter search space
        learning_rate = trial.suggest_float("learning_rate", 4e-5, 8e-4, log=True)
        learning_rate_decay = trial.suggest_float("learning_rate_decay", 0.99, 0.999, log=True)
        gamma = trial.suggest_float("gamma", 0.99, 0.999, log=True)
        epsilon_decay = trial.suggest_float("epsilon_decay", 0.999, 0.99999, log=True)
        epsilon_min = trial.suggest_float("epsilon_min", 0.05, 0.2, log=True)
        buffer_size = trial.suggest_categorical("buffer_size", [100_000, 250_000, 500_000])
        batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
        
        
        # Log params with MLflow for this specific trial
        mlflow.log_params(trial.params)

        # Instantiate and run the trainer with the suggested hyperparameters
        trainer = Trainer(
            learning_rate=learning_rate,
            learning_rate_decay=learning_rate_decay,
            gamma=gamma,
            epsilon_decay=epsilon_decay,
            epsilon_min=epsilon_min,
            buffer_size=buffer_size,
            batch_size=batch_size,
            num_episodes=5000,  # Use fewer episodes for faster tuning
            eval_freq=1000,
            seed=42,  # Use a fixed seed for all trials for fair comparison
        )

        final_win_rate = trainer.train()

        # Log the final metric that we are optimizing
        mlflow.log_metric("final_win_rate", final_win_rate)

        return final_win_rate


def main():
    parser = argparse.ArgumentParser(description="Tune hyperparameters for the DQN agent.")
    parser.add_argument(
        "--trials", type=int, default=20, help="Number of Optuna trials to run."
    )
    args = parser.parse_args()

    # Set the experiment for the overall tuning process
    mlflow.set_experiment("Connect4 Hyperparameter Tuning")

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=args.trials)

    print("--- Optuna Study Best Trial ---")
    print(f"  Value (Max Win Rate): {study.best_trial.value:.4f}")
    print("  Best Parameters:")
    for key, value in study.best_trial.params.items():
        print(f"    {key}: {value}")
    
    # You can also view all trials in the MLflow UI under the "Connect4 Hyperparameter Tuning" experiment


if __name__ == "__main__":
    main()
