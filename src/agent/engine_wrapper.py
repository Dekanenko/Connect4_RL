import numpy as np
from src.game_engine.connect4_engine import Connect4Engine


class Connect4Env:
    def __init__(self):
        self.engine = Connect4Engine()

    @property
    def state_shape(self):
        return 2, self.engine.ROWS, self.engine.COLS

    @property
    def actions_num(self):
        return self.engine.COLS

    def reset(self):
        self.engine.reset()
        return self._get_state()

    def step(self, action):
        acting_player = self.engine.current_player
        valid, done, winner = self.engine.step(action)
        if not valid:
            return self._get_state(), -2.0, True, {}

        reward = -1.0
        if done:
            if winner == self.engine.DRAW:
                reward = 0.0
            elif winner == acting_player:
                reward = 1.0
            else:
                reward = -1.0

        return self._get_state(), reward, done, {}

    def _get_state(self):
        current_player = self.engine.current_player
        board = self.engine.get_board()

        me = (board == current_player).astype(np.float32)
        opp = ((board != current_player) & (board != 0)).astype(np.float32)

        return np.stack([me, opp], axis=0)
