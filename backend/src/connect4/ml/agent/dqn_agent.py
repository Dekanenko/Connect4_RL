import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import copy

class ConvNet(nn.Module):
    def __init__(self, state_shape: tuple[int, int, int], actions_num: int):
        super(ConvNet, self).__init__()
        self.state_shape = state_shape
        self.actions_num = actions_num
        
        # Convolutional layers
        self.conv = nn.Sequential(
            nn.Conv2d(self.state_shape[0], 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        
        # Calculate the flattened size after the convolutional layers
        conv_out_size = self._get_conv_out(state_shape)
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 512),
            nn.ReLU(),
            nn.Linear(512, self.actions_num),
        )

    def _get_conv_out(self, shape: tuple[int, int, int]) -> int:
        """
        Calculates the output size of the convolutional layers to inform the
        input size of the first fully connected layer.
        """
        o = self.conv(torch.zeros(1, *shape))
        return int(np.prod(o.size()))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Defines the forward pass of the network.
        """
        conv_out = self.conv(x).view(x.size()[0], -1)  # Flatten the output
        return self.fc(conv_out)


class DQNAgent:
    def __init__(
        self,
        state_shape: tuple[int, int, int],
        actions_num: int,
        gamma: float = 0.99,
        learning_rate: float = 1e-3,
        device: str = "cpu",
    ):
        self.state_shape = state_shape
        self.actions_num = actions_num
        self.gamma = gamma
        self.device = device

        # Main Q-network
        self.model = ConvNet(state_shape, actions_num).to(device)

        # Target Q-network (frozen)
        self.target_model = copy.deepcopy(self.model).to(device)
        self.target_model.eval()
        for p in self.target_model.parameters():
            p.requires_grad = False

        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

    def _get_valid_actions_from_state(self, state: torch.Tensor) -> np.ndarray:
        """
        Calculates valid actions directly from the state tensor.
        A column is valid if the top-most cell is empty (0).
        The state tensor has shape (2, 6, 7)
        """
        full_board = state.sum(axis=0)
        top_row = full_board[0]
        return np.where(top_row.cpu().numpy() == 0)[0]

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.model(state)

    def act(self, state: torch.Tensor, epsilon: float) -> int:
        """
        Epsilon-greedy action selection with now-correct invalid-action masking.
        """
        valid_actions = self._get_valid_actions_from_state(state)

        if not valid_actions.any():
            return 0 # Safeguard

        if np.random.rand() < epsilon:
            return int(np.random.choice(valid_actions))

        with torch.no_grad():
            q_values = self.forward(state.unsqueeze(0)).squeeze(0)
            invalid_actions = [a for a in range(self.actions_num) if a not in valid_actions]
            q_values[invalid_actions] = -float("inf")
            return int(q_values.argmax().item())

    # -------------------------------------------------
    # Training
    # -------------------------------------------------

    def train_step(self, batch):
        """
        batch = (states, actions, rewards, next_states, dones)
        """
        states, actions, rewards, next_states, dones = batch

        states = states.to(self.device)
        next_states = next_states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        dones = dones.to(self.device)

        # Q(s, a)
        q_values = self.forward(states)
        q_sa = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Bellman target
        with torch.no_grad():
            next_q_values = self.target_model(next_states)

            max_next_q = next_q_values.max(dim=1)[0]
            # The reward is from the perspective of the player who made the move.
            # Since the `next_state` is from the opponent's perspective, we need to think about the value
            # of that state from the opponent's point of view. The best the opponent can do (max_next_q)
            # is bad for us, so we should negate it.
            targets = rewards - self.gamma * max_next_q * (1.0 - dones)

        # Loss & optimization
        loss = self.loss_fn(q_sa, targets)

        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), 10.0)
        self.optimizer.step()

        return loss.item()

    # -------------------------------------------------
    # Target network update
    # -------------------------------------------------

    def update_target(self):
        """
        Hard update of target network
        """
        self.target_model.load_state_dict(self.model.state_dict())
