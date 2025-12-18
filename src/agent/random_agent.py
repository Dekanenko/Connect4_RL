import random
from src.agent.engine_wrapper import Connect4Env

class RandomAgent:
    def __init__(
        self,
        env: Connect4Env,
    ):
        self.env = env

    def act(self) -> int:
        """
        Epsilon-greedy action selection with invalid-action masking
        """
        valid_actions = self.env.engine.get_valid_actions()
        return random.choice(valid_actions)
