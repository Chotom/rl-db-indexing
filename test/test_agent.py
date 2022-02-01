import unittest

from db_env.DatabaseEnvironment import DatabaseEnvironment
from db_env.mock.RandomTpchMockDatabase import RandomTpchMockDatabase
from db_env.mock.MockDatabase import MockDatabase
from agent.Agent import Agent
from agent.AgentActionFeatures import Agent as AgentAF


class TestAgent(unittest.TestCase):
    def test_train(self):
        db = MockDatabase()
        db_env = DatabaseEnvironment(db, True)
        agent = AgentAF(db_env)

        agent.train(50, 50)
        print(db_env.render())

    def test_RandomTpchMockDatabase(self):
        db = RandomTpchMockDatabase()
        db_env = DatabaseEnvironment(db)
        agent = Agent(db_env)

        agent.train(100, 50)
        print(db_env.render())

    def test_RandomAgentAFTpchMockDatabase(self):
        db = RandomTpchMockDatabase()
        db_env = DatabaseEnvironment(db)
        agent = AgentAF(db_env)

        agent.train(100, 50)
        print(db_env.render())
