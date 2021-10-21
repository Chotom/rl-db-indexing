# rl-db-indexing

[![License](https://img.shields.io/github/license/Chotom/rl-db-indexing)](https://github.com/Chotom/rl-db-indexing/blob/main/LICENSE)

Database indexes tuning with agent using reinforcement learning techniques

## Setup

Create venv and install packages with:

```shell
pip install -r requirements.txt
```

## Project structure

### db_env

Package with database environment for agent.

DatabaseEnvironment.py
```python
from db_env.mock.MockDatabase import MockDatabase
from db_env.DatabaseEnvironment import DatabaseEnvironment

# Example usage
db = MockDatabase()
db_env = DatabaseEnvironment(db)

# Methods
db_env.step(db_env.action_space.sample())
db_env.render()
db_env.reset()
```

#### tpch

Package with concrete database class for tpch benchmark.

#### mock

Package with example mock database for tests with stored sample data.

### tests
Tests for procject.