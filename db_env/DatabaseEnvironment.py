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
        self.action_space = spaces.Discrete(len(db.action_mapper))
        # self.observation_space: The Space object corresponding to valid observations

    def available_actions(self):
        pass

    def step(self, action):
        self._db.execute_action(action)
        observation = self._db.get_current_mapped_database()
        reward = None

        # Return tuple (observation, reward, done, info).
        # Where:
        #     observation (object): agent's observation of the current environment
        #     reward (float) : amount of reward returned after previous action
        #     done (bool): whether the episode has ended, in which case further step() calls will return undefined results
        #     info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)

        return observation, reward, False, ''

    def reset(self):
        self._db.reset_indexes()
        return self._db.get_current_mapped_database()

    def render(self, mode='ansi'):
        out = StringIO()

        out.write('Database current state\n')
        for table_name, table in self._db.get_current_mapped_database().items():
            out.write(f'\t{table_name}:\n')
            for col_name, is_indexed in table.items():
                out.write(f'\t\t{col_name} - is indexed: {is_indexed}\n')
            out.write('\n')

        out.write('Actions space\n')
        for action_number, action_type in enumerate(self._db.action_mapper):
            out.write(f'\taction no. {action_number}: {action_type}\n')

        with closing(out):
            return out.getvalue()
