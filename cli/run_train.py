from db_env.tpch.TpchDatabase import TpchDatabase
from db_env.DatabaseEnvironment import DatabaseEnvironment
from agent.AgentActionFeatures import Agent

if __name__ == '__main__':
    db = TpchDatabase()
    env = DatabaseEnvironment(db)
    agent = Agent(env)

    env.render()
    agent.train(50, 100)
    env.render()
