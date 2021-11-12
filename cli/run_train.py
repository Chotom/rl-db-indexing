from db_env.tpch.TpchDatabase import TpchDatabase
from db_env.DatabaseEnvironment import DatabaseEnvironment
from agent.Agent import Agent

if __name__ == '__main__':
    db = TpchDatabase()
    env = DatabaseEnvironment(db)
    agent = Agent(env)

    agent.train(10, 10)