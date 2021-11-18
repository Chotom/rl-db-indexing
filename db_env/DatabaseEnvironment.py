import random

import gym as gym
import numpy as np
import pandas as pd
from gym import spaces
from contextlib import closing
from io import StringIO
from typing import List

from db_env.Database import Database
from shared_utils.consts import PROJECT_DIR

REWARDS_FILE = f'{PROJECT_DIR}/data/reward_cache.csv'


class DatabaseEnvironment(gym.Env):
    metadata = {'render.modes': ['ansi']}

    def __init__(self, db: Database, use_cache: bool = False):
        super(DatabaseEnvironment, self).__init__()

        self._db = db
        self._use_cache = use_cache
        self._reward_cache: dict[int, float] = {}
        self._initial_state_reward: float = -np.inf

        self.action_space = spaces.Discrete(len(db.action_mapper))
        self.observation_space = spaces.MultiBinary(int(self.action_space.n / 2))

    def step(self, action):
        self._db.execute_action(action)
        return (self._get_observation(),  # Observation
                self._get_reward(),  # Reward
                False,  # is Episode done
                {'initial_state_reward': self._initial_state_reward})  # Additional info

    def reset(self):
        self._db.reset_indexes()
        self._initial_state_reward = self._db.execute_benchmark()
        return self._get_observation()

    def render(self, mode='ansi'):
        out = StringIO()
        out.write('Environment observation:\n')
        out.write(f'\t{self._get_observation()}\n\n')
        out.write('Database current state:\n')
        for table_name, table in self._db.state.items():
            out.write(f'\t{table_name}:\n')
            for col_name, is_indexed in table.items():
                out.write(f'\t\t{col_name} - is indexed: {is_indexed}\n')
            out.write('\n')
        with closing(out):
            return out.getvalue()

    def get_action_meanings(self):
        """:return: Action meanings in array where index is number of action"""
        return self._db.action_mapper

    def _get_observation(self) -> List[bool]:
        """:return: Map database state to environment observation"""
        observation: list[bool] = []
        for table in self._db.state.values():
            for is_indexed in table.values():
                observation.append(int(is_indexed))
        return observation

    def _get_reward(self) -> float:
        """
        Search for saved reward in dict by current state, or execute benchmark
        to measure and save result.

        :return: Measured or saved result from benchmark
        """
        if not self._use_cache:
            return self._db.execute_benchmark()

        key = str(self._get_observation())
        if key in self._reward_cache.keys():
            return self._reward_cache[key]
        else:
            reward = self._db.execute_benchmark()
            self._reward_cache[key] = reward
            pd.DataFrame.from_dict(self._reward_cache, orient='index').to_csv(REWARDS_FILE)
            return reward
