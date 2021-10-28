import random
import numpy as np
import gym as gym

from db_env.DatabaseEnvironment import DatabaseEnvironment

class Agent:

    # todo: get count from environment maybe
    features_count: int = 3
    actions_count: int = 3


    def __init__(self, env: DatabaseEnvironment):
        self._env = env
        self.exploration_probability = 0.9
        self.learning_rate = 0.01
        self.discount_factor = 0.8
        self._weights = [np.zeros(self.features_count + 1)
                         for _ in range(self._env.action_space.n)]
        """Estimated weights of features and bias for every action."""

    def train(self, episode_count: int, steps_per_episode: int):
        for episode in range(episode_count):
            print(f'Starting episode {episode}: ')
            print(f'Current weights: {self._weights}')

            state = self._env.reset()

            for step in range(steps_per_episode):
                print(f'Step {step} of episode {episode}')
                print(f'Current weights: {self._weights}')
                print(f'Current state:')
                print(state)

                action = self._choose_action(state)
                print(f'Taking action:')
                print(action)

                next_state, reward, _, _ = self._env.step(action)
                print(f'Moved to:')
                print(next_state)
                print(f'Reward: {reward}')

                # choose max from q(next_state, unknown_action) over action
                self._update_weights(state, action, reward, next_state)

                state = next_state

            self._reduce_exploration_probability()

    # f_i(s, a) = f_i(s') = if a == changes_index(i), then new_i else s_i
    # max_q = q(s')

    def _update_weights(self, state, action, reward, next_state):
        state_features = self._get_features_from_state(state)
        # Add bias = 1
        features = np.array([1] + state_features)

        max_action, max_q = self._get_max_action(next_state)

        print(f'old weights: {self._weights}')

        # w = w + a(r + y(max q) - w^T * F(s)) * F(s)
        approx_q = self._weights[action] @ features
        self._weights[action] += (self.learning_rate
                                  * (reward + self.learning_rate * max_q - approx_q)
                                  * features)

        print(f'new weights: {self._weights}')

    def _get_max_action(self, state):
        max_q = float('-inf')
        max_action = None

        # for each possible action
        for action in self._possible_actions(state):
            # calculate q
            q = self._calculate_q_value(state, action)
            # save if maximal
            if max_q < q:
                max_q = q
                max_action = action

        return max_action, max_q

    def _calculate_q_value(self, state, action):
        # Add bias = 1
        features = np.array([1] + self._get_features_from_state(state))

        return self._weights[action] @ features

    # Q(s, a) = V(s') = w^t * features(s')

    def _possible_actions(self, state) -> list[int]:
        features = self._get_features_from_state(state)
        possible_actions = []
        for index, is_indexed in enumerate(features):
            possible_action = index*2 + (not is_indexed)
            possible_actions.append(possible_action)

        return possible_actions

    def _choose_action(self, state):
        if random.random() < self.exploration_probability:
            # return random action with probability epsilon
            return random.choice(self._possible_actions(state))
        # return best action with probability 1-epsilon
        max_action, _ = self._get_max_action(state)
        return max_action

    def _get_features_from_state(self, state) -> list[bool]:
        return [is_indexed for table in state.values() for is_indexed in table.values()]

    def _reduce_exploration_probability(self):
        self.exploration_probability = 0.75 * self.exploration_probability