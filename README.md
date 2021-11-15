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

### Prepare server (without docker)

Install mysql server (version 8)

Make sure root has access to



---

### Prepare client (without docker)

Install mysql client (version 8), gcc, make, python3 (minimal version 3.8)

```shell
apt install mysql
```

Install virtualenv python package

```shell
pip install virtualenv
```
Move project to desired folder

Create virtual environment (for example inside project directory)

```shell
virtualenv venv
```

Save project path to $PYTHONPATH

```shell
echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/project/"' >> venv/bin/activate
```

Activate virtual environment

```shell
source venv/bin/activate
```

Make sure python version is at least 3.8

```shell
python --version
```

Install python requirements (inside project folder)

```shell
pip install -r requirements.txt
```

Patch dbgen

```shell
python cli/patch_dbgen.py
```

Compile dbgen
```shell
make -C /path/to/project/dbgen
```

Initiate environment - populate database with generated data (this will also generate 4000 refresh function datasets for benchmarking)
```shell
python cli/initiate_environment.py
```

You can train agent now, for example:
```shell
nohup python cli/train_agent.py &> data/train.log
```

In case you want to run single benchmark on current database configuration
```shell
python cli/run_benchmark.py
```

Or if you want to reset database (without generating data for benchmark again)
```shell
python cli/run_benchmark.py
```

---

## Important!

You should not interfere with file

path/to/project/data/rf_db_index.txt

Keep in mind that every executed refresh pair should increment number stored in file

path/to/project/data/rf_db_index.txt

After refresh pair number 4000 database should be in its initial state (Note that this still hasn't been tested) - rf_db_index.txt should contain 1.

Otherwise, you will lose information about current database state, which may (and sooner or later will) lead to errors and force you to stop training and reset database.

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