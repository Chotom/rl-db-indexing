from shared_utils.consts import PROJECT_DIR

SCALE_FACTOR = 0.1
"""Database size in GB"""

STREAM_COUNT = 2
"""Parallel stream number in throughput test"""

MAX_REFRESH_FILE_INDEX = 2000
"""Max refresh file index from tpc-h documentation"""

DB_GENERATOR_TOOL = f'{PROJECT_DIR}/dbgen'
"""Path to dbgen tpch tool"""

DB_DATA_DIR = f'{PROJECT_DIR}/data/db_data'
DB_QUERIES_DIR = f'{PROJECT_DIR}/data/db_queries'
DB_REFRESH_DIR = f'{PROJECT_DIR}/data/db_refresh'
DB_REFRESH_ID = f'{PROJECT_DIR}/data/rf_file_index.txt'

TPCH_MUTABLE_COLUMNS = [
    ('nation', 'n_name'),
    ('nation', 'n_comment'),
    ('region', 'r_name'),
    ('region', 'r_comment'),
    ('part', 'p_name'),
    ('part', 'p_mfgr'),
    ('part', 'p_brand'),
    ('part', 'p_type'),
    ('part', 'p_size'),
    ('part', 'p_container'),
    ('part', 'p_retailprice'),
    ('part', 'p_comment'),
    ('supplier', 's_name'),
    ('supplier', 's_address'),
    ('supplier', 's_phone'),
    ('supplier', 's_acctbal'),
    ('supplier', 's_comment'),
    ('partsupp', 'ps_availqty'),
    ('partsupp', 'ps_supplycost'),
    ('partsupp', 'ps_comment'),
    ('customer', 'c_name'),
    ('customer', 'c_address'),
    ('customer', 'c_phone'),
    ('customer', 'c_acctbal'),
    ('customer', 'c_mktsegment'),
    ('customer', 'c_comment'),
    ('orders', 'o_orderstatus'),
    ('orders', 'o_totalprice'),
    ('orders', 'o_orderdate'),
    ('orders', 'o_orderpriority'),
    ('orders', 'o_clerk'),
    ('orders', 'o_shippriority'),
    ('orders', 'o_comment'),
    ('lineitem', 'l_quantity'),
    ('lineitem', 'l_extendedprice'),
    ('lineitem', 'l_discount'),
    ('lineitem', 'l_tax'),
    ('lineitem', 'l_returnflag'),
    ('lineitem', 'l_linestatus'),
    ('lineitem', 'l_shipdate'),
    ('lineitem', 'l_commitdate'),
    ('lineitem', 'l_receiptdate'),
    ('lineitem', 'l_shipinstruct'),
    ('lineitem', 'l_shipmode'),
    ('lineitem', 'l_comment')
]
