import random
import csv
import signal
from typing import List, Tuple

import numpy as np
import pandas as pd

from db_env.DatabaseEnvironment import DatabaseEnvironment
from shared_utils.consts import PROJECT_DIR
from shared_utils.utils import create_logger

AGENT_CSV_FILE = f'{PROJECT_DIR}/data/agent_history.csv'
WEIGHTS_FILE = f'{PROJECT_DIR}/data/weights.csv'


class Agent:
    def __init__(self, env: DatabaseEnvironment):
        random.seed(1)
        np.random.seed(1)
        self._log = create_logger('agent')
        self._env = env
        self.exploration_probability = 0.9
        self.exploration_probability_discount = 0.75
        self.learning_rate = 0.01
        self.discount_factor = 0.8
        self._experience_memory_max_size = np.inf
        self._experience_replay_count = 32

        self._weights = np.random.rand(self._env.action_space.n, self._env.observation_space.n + 1)
        """Estimated weights of features with bias for every action."""
        self._experience_memory: List[Tuple[List[int], int, float, List[int]]] = []
        self.dict_info = {
            'episode': int,
            'step': int,
            'state': List[bool],
            'action': int,
            'reward': float,
            'next_state': List[bool],
            'q': float,
            'max_a': int,
            'max_q': float,
            'td_target': float,
            'td_error': float,
            'total_reward': float,
            'exploration_probability': float,
            'random_action': bool,
            'initial_state_reward': float
        }

        self._pause_request = False

        def signal_handler(sig, frame):
            self._log.info('CTRL+C pressed - pausing training requested')
            self._pause_request = True

        signal.signal(signal.SIGINT, signal_handler)

    def train(self, episode_count: int, steps_per_episode: int):
        with open(AGENT_CSV_FILE, 'w', newline='') as file:
            wr = csv.writer(file)
            wr.writerow(self.dict_info.keys())

        for episode in range(episode_count):
            state = self._env.reset()
            total_reward = 0.0

            for step in range(steps_per_episode):
                self._log.info(f'EPISODE {episode} - STEP {step} '
                               f'({(episode_count - episode) * steps_per_episode - step - 1} more steps to go)')

                action = self._choose_action(state)
                next_state, reward, _, info = self._env.step(action)
                total_reward += reward
                previous_weights = self._weights.copy()
                self._update_weights(state, action, reward, next_state, self._weights)
                self._save_agent_information(episode, step, state, next_state, action, reward, total_reward, info)
                self._experience_replay(previous_weights)
                self._experience_append(state, action, reward, next_state)
                self._save_agent_weights()
                state = next_state

                if self._pause_request:
                    return

            self._reduce_exploration_probability()

    def _experience_append(self, state, action, reward, next_state):
        self._experience_memory.append((state, action, reward, next_state))

        if len(self._experience_memory) > self._experience_memory_max_size:
            self._experience_memory.pop(0)

    def _experience_replay(self, previous_weights):
        samples_count = min(len(self._experience_memory), self._experience_replay_count)
        samples = random.sample(self._experience_memory, k=samples_count)

        for state, action, reward, next_state in samples:
            self._update_weights(state, action, reward, next_state, previous_weights)

    def _update_weights(self, state, action, reward, next_state, weights):
        biased_features = np.array([1] + state)
        max_action, max_q = self._get_max_action(next_state)

        approx_q = weights[action] @ biased_features
        td_target = reward + self.discount_factor * max_q
        td_error = td_target - approx_q

        # w = w + a(r + y(max q) - w^T * F(s)) * F(s)
        self._weights[action] += self.learning_rate * td_error * biased_features

        self.dict_info['q'] = approx_q
        self.dict_info['max_a'] = max_action
        self.dict_info['max_q'] = max_q
        self.dict_info['td_target'] = td_target
        self.dict_info['td_error'] = td_error

    def _get_max_action(self, state):
        max_q = float('-inf')
        max_action = None

        for action in self._possible_actions(state):
            q = self._calculate_q_value(state, action)
            if max_q < q:
                max_q = q
                max_action = action
        return max_action, max_q

    def _calculate_q_value(self, state, action):
        """:return cartesian product of feature weights and state features with bias"""
        return self._weights[action] @ np.array([1] + state)

    def _possible_actions(self, state) -> List[int]:
        return [i * 2 + (not is_indexed) for i, is_indexed in enumerate(state)]

    def _choose_action(self, state):
        """
        :param state: current environment state
        :return: random action with probability epsilon otherwise best action with probability 1-epsilon
        """

        self.dict_info['random_action'] = False
        self.dict_info['exploration_probability'] = self.exploration_probability

        if random.random() < self.exploration_probability:
            self.dict_info['random_action'] = True
            return random.choice(self._possible_actions(state))

        max_action, _ = self._get_max_action(state)
        return max_action

    def _reduce_exploration_probability(self):
        self.exploration_probability = self.exploration_probability_discount * self.exploration_probability

    def _save_agent_information(self, episode, step, state, next_state, action, reward, total_reward, info):
        self.dict_info['episode'] = episode
        self.dict_info['step'] = step
        self.dict_info['state'] = state
        self.dict_info['next_state'] = next_state
        self.dict_info['action'] = action
        self.dict_info['reward'] = reward
        self.dict_info['total_reward'] = total_reward
        self.dict_info['initial_state_reward'] = info['initial_state_reward']

        with open(AGENT_CSV_FILE, 'a', newline='') as file:
            wr = csv.writer(file)
            wr.writerow(self.dict_info.values())

    def _save_agent_weights(self):
        pd.DataFrame(self._weights).to_csv(WEIGHTS_FILE, index=False)
