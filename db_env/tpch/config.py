from shared_utils.consts import PROJECT_DIR

SCALE_FACTOR = 0.1
"""Database size in GB"""

STREAM_COUNT = 2
"""Parallel stream number in throughput test"""

MAX_REFRESH_FILE_INDEX = 4000
"""Max refresh file index from tpc-h documentation"""

DB_GENERATOR_TOOL = f'{PROJECT_DIR}/dbgen'
"""Path to dbgen tpch tool"""

DB_DATA_DIR = f'{PROJECT_DIR}/data/db_data'
DB_QUERIES_DIR = f'{PROJECT_DIR}/data/db_queries'
DB_REFRESH_DIR = f'{PROJECT_DIR}/data/db_refresh'
DB_REFRESH_ID = f'{PROJECT_DIR}/data/rf_file_index.txt'
