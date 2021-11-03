import unittest

from db_env.DatabaseEnvironment import DatabaseEnvironment
from db_env.mock.MockDatabase import MockDatabase


class TestDatabaseEnvironment(unittest.TestCase):
    def setUp(self) -> None:
        self.db = MockDatabase()
        self.db_env = DatabaseEnvironment(self.db)

    def test_action_space_sample(self):
        self.assertTrue(0 <= self.db_env.action_space.sample() <= len(self.db.action_mapper))

    def test_observation_space(self):
        self.assertTrue(self.db_env.observation_space['table1']['column1'].sample() in [0, 1])
        self.assertTrue(self.db_env.observation_space['table1']['column2'].sample() in [0, 1])
        self.assertTrue(self.db_env.observation_space['table2']['column1'].sample() in [0, 1])
        print(self.db_env.observation_space)

    def test_render(self):
        render = self.db_env.render()
        self.assertIsNotNone(render)
        print(render)

    def test_reset(self):
        initial_state = self.db_env.reset()
        for table_name, cols in initial_state.items():
            for col_name in cols:
                self.assertEqual(initial_state[table_name][col_name], 0)


if __name__ == '__main__':
    unittest.main()
