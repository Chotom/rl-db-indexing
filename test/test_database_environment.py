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
        self.assertTrue(self.db_env.observation_space.sample()[0] in [0, 1])
        self.assertTrue(self.db_env.observation_space.sample()[1] in [0, 1])
        self.assertTrue(self.db_env.observation_space.sample()[2] in [0, 1])

    def test_render(self):
        render = self.db_env.render()
        self.assertIsNotNone(render)
        print(render)

    def test_get_action_meaning(self):
        action_meanings = self.db_env.get_action_meanings()
        assert(action_meanings[0] == ('table1', 'column1', 'DROP INDEX'))
        assert(action_meanings[3] == ('table1', 'column2', 'CREATE INDEX'))

    def test_reset(self):
        initial_state = self.db_env.reset()
        self.assertEqual(initial_state[0], 0)
        self.assertEqual(initial_state[1], 0)
        self.assertEqual(initial_state[2], 0)


if __name__ == '__main__':
    unittest.main()
