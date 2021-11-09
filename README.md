# rl-db-indexing

Database indexes tuning with agent using reinforcement learning techniques

[![License](https://img.shields.io/github/license/Chotom/rl-db-indexing)](https://github.com/Chotom/rl-db-indexing/blob/main/LICENSE)

## Setup

How to train an agent and set up an environment for TPC-H database with Docker.

### Prepare tpch database

1. In '*./db_env/tpch/tpch_tools*'  paste tpc-h-tool.zip downloaded from tpc website (version
   3.0.0): [download link](http://tpc.org/tpc_documents_current_versions/download_programs/tools-download-request5.asp?bm_type=TPC-H&bm_vers=3.0.0&mode=CURRENT-ONLY "tpch tools")


2. Define tpch database size (in GB) in *./db_env/tpch/config.py*

```python
SCALE_FACTOR = 0.1  # Preferred 1 or 0.1 for local usage
```

3. Start mysql server and client

```shell
docker-compose up -d
```

4. Generate data and load database to mysql_server in container

```shell
docker-compose exec client python3 /project/db_env/tpch/TpchGenerator.py
```

---

### Prepare benchmark

---

### Train agent

---

## Project structure

### data

Directory to store project datafiles and data analysis.

### agent

Package with agent to train

### db_env

Package with database environment for agent.

### shared_utils

Package with utilities functions and variables to use in project.

### test

Run tests with code coverage:

```shell
coverage run -m unittest
coverage report
```