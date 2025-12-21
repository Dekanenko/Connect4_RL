import random
import numpy as np

from connect4.game.engine_wrapper import Connect4Env
from connect4.game.engine import Connect4Engine

class RuleBasedAgent:
    def __init__(self, env: Connect4Env, player_id: int):
        self.env = env
        self.player_id = player_id
        self.opponent_id = (
            Connect4Engine.PLAYER_2
            if self.player_id == Connect4Engine.PLAYER_1
            else Connect4Engine.PLAYER_1
        )

    def act(self) -> int:
        valid_actions = self.env.engine.get_valid_actions()
        current_board = self.env.engine.get_board()

        # 1. Check for a winning move for myself
        for action in valid_actions:
            board_copy = current_board.copy()
            row = self.env.engine._get_next_empty_row(action)
            board_copy[row, action] = self.player_id
            if self.env.engine.check_win_on_board(board_copy, self.player_id):
                return action

        # 2. Check for a winning move for the opponent and block it
        for action in valid_actions:
            board_copy = current_board.copy()
            row = self.env.engine._get_next_empty_row(action)
            board_copy[row, action] = self.opponent_id
            if self.env.engine.check_win_on_board(board_copy, self.opponent_id):
                return action

        # 3. Otherwise, return a random move
        return random.choice(valid_actions)

