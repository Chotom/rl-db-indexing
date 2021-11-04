import unittest

from db_env.DatabaseEnvironment import DatabaseEnvironment
from db_env.mock.MockDatabase import MockDatabase
from agent.Agent import Agent


class TestAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.db = MockDatabase()
        self.db_env = DatabaseEnvironment(self.db)
        self.agent = Agent(self.db_env)

    def test_train(self):
        self.agent.train(20, 200)

        print(self.agent._weights)
        print(self.db_env.render())


    # def test_action_space_sample(self):
    #     self.assertTrue(0 <= self.db_env.action_space.sample() <= len(self.db.action_mapper))
    #
    # def test_render(self):
    #     render = self.db_env.render()
    #     self.assertIsNotNone(render)
    #     print(render)
    #
    # def test_reset(self):
    #     initial_state = self.db_env.reset()
    #     for table_name, cols in initial_state.items():
    #         for col_name in cols:
    #             self.assertEqual(initial_state[table_name][col_name], 0)
