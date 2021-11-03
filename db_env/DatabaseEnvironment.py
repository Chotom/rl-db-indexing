import gym as gym
from contextlib import closing
from io import StringIO
from gym import spaces

from db_env.Database import Database


class DatabaseEnvironment(gym.Env):
    metadata = {'render.modes': ['ansi']}

    def __init__(self, db: Database):
        super(DatabaseEnvironment, self).__init__()

        self._db = db
        self._reward_cache: dict[int, float] = {}

        self.action_space = spaces.Discrete(len(db.action_mapper))
        self.observation_space = self._get_observation_space() # todo: change to Multibinary

    def step(self, action):
        self._db.execute_action(action)
        return (self._db.state,  # Observation
                self._get_reward(),  # Reward
                False,  # is Episode done
                '{}')  # Additional info

    def reset(self):
        self._db.reset_indexes()
        return self._db.state

    def render(self, mode='ansi'):
        out = StringIO()

        out.write('Database current state\n')
        for table_name, table in self._db.state.items():
            out.write(f'\t{table_name}:\n')
            for col_name, is_indexed in table.items():
                out.write(f'\t\t{col_name} - is indexed: {is_indexed}\n')
            out.write('\n')

        out.write('Actions space\n')
        for action_number, action_type in enumerate(self._db.action_mapper):
            out.write(f'\taction no. {action_number}: {action_type}\n')

        with closing(out):
            return out.getvalue()

    def _get_observation_space(self) -> spaces.Dict:
        """:return: Created possible space for observations (states)"""
        db_state_dict = {}
        for table_name, table in self._db.state.items():
            table_dict = {}
            for col_name in table:
                # 0 - not indexed, 1 - indexed column
                table_dict[col_name] = spaces.Discrete(2)
            db_state_dict[table_name] = spaces.Dict(table_dict)
        return spaces.Dict(db_state_dict)

    def _get_reward(self) -> float:
        """
        Search for saved reward in dict by current state, or execute benchmark
        to measure and save result.

        :return: Measured or saved result from benchmark
        """

        if key := hash(str(self._db.state)) in self._reward_cache.keys():
            return self._reward_cache[key]
        else:
            reward = self._db.execute_benchmark()
            self._reward_cache[key] = reward
            return reward
