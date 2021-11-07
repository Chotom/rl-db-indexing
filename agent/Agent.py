import random
import csv
import numpy as np

from db_env.DatabaseEnvironment import DatabaseEnvironment
from shared_utils.consts import PROJECT_DIR

AGENT_CSV_FILE = f'{PROJECT_DIR}/data/agent_history.csv'
WEIGHTS_FILE = f'{PROJECT_DIR}/data//data/weights.dat'


class Agent:
    def __init__(self, env: DatabaseEnvironment):
        self._env = env
        self.exploration_probability = 0.9
        self.learning_rate = 0.01
        self.discount_factor = 0.8
        self._weights = [np.zeros(self._env.observation_space.n + 1)
                         for _ in range(self._env.action_space.n)]
        """Estimated weights of features with bias for every action."""

        self.dict_info = {
            'episode':                  int,
            'step':                     int,
            'state':                    list[bool],
            'action':                   int,
            'reward':                   float,
            'next_state':               list[bool],
            'q':                        float,
            'max_a':                    int,
            'max_q':                    int,
            'total_reward':             float,
            'exploration_probability':  float,
            'random_action':            bool
        }

    def train(self, episode_count: int, steps_per_episode: int):
        with open(AGENT_CSV_FILE, 'w', newline='') as file:
            wr = csv.writer(file)
            wr.writerow(self.dict_info.keys())

        for episode in range(episode_count):
            state = self._env.reset()
            total_reward = 0.0

            for step in range(steps_per_episode):
                action = self._choose_action(state)
                next_state, reward, _, _ = self._env.step(action)
                total_reward += reward

                self._update_weights(state, action, reward, next_state)
                self._save_agent_information(step, episode, state, next_state, action, reward, total_reward)

                state = next_state

            self._reduce_exploration_probability()

    def _update_weights(self, state, action, reward, next_state):
        biased_features = np.array([1] + state)
        max_action, max_q = self._get_max_action(next_state)

        # w = w + a(r + y(max q) - w^T * F(s)) * F(s)
        approx_q = self._weights[action] @ biased_features
        self._weights[action] += (self.learning_rate
                                  * (reward + self.learning_rate * max_q - approx_q)
                                  * biased_features)

        self.dict_info['q'] = approx_q
        self.dict_info['max_a'] = max_action
        self.dict_info['max_q'] = max_q

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

    def _possible_actions(self, state) -> list[int]:
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
        self.exploration_probability = 0.75 * self.exploration_probability

    def _save_agent_information(self, episode, step, state, next_state, action, reward, total_reward):
        self.dict_info['episode'] = episode
        self.dict_info['step'] = step
        self.dict_info['state'] = state
        self.dict_info['next_state'] = next_state
        self.dict_info['action'] = action
        self.dict_info['reward'] = reward
        self.dict_info['total_reward'] = total_reward

        with open(AGENT_CSV_FILE, 'a', newline='') as file:
            wr = csv.writer(file)
            wr.writerow(self.dict_info.values())
