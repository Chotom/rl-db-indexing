import unittest

from db_env.DatabaseEnvironment import DatabaseEnvironment
from db_env.mock.RandomTpchMockDatabase import RandomTpchMockDatabase
from db_env.mock.MockDatabase import MockDatabase
from agent.Agent import Agent


class TestAgent(unittest.TestCase):
    def test_train(self):
        db = MockDatabase()
        db_env = DatabaseEnvironment(db, True)
        agent = Agent(db_env)

        agent.train(20, 200)
        print(db_env.render())

    def test_RandomTpchMockDatabase(self):
        db = RandomTpchMockDatabase()
        db_env = DatabaseEnvironment(db, True)
        agent = Agent(db_env)

        agent.train(50, 100)
        print(db_env.render())
