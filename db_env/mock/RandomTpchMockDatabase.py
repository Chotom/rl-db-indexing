import random
from typing import List

from db_env import Benchmark
from db_env.Database import Database


class RandomTpchMockDatabase(Database):
    """
    Simple example database class for tests with stored sample data. Does not
    connect with any database, all operations are simulated and perform results
    are already defined.

    Possible states and their benchmark results are based on reward array.
    """
    _database_schema_as_dict = {
        'nation': {
            'n_name': False,
            'n_comment': False
        },
        'region': {
            'r_name': False,
            'r_comment': False
        },
        'part': {
            'p_name': False,
            'p_mfgr': False,
            'p_brand': False,
            'p_type': False,
            'p_size': False,
            'p_container': False,
            'p_retailprice': False,
            'p_comment': False
        },
        'supplier': {
            's_name': False,
            's_address': False,
            's_phone': False,
            's_acctbal': False,
            's_comment': False
        },
        'partsupp': {
            'ps_availqty': False,
            'ps_supplycost': False,
            'ps_comment': False
        },
        'customer': {
            'c_name': False,
            'c_address': False,
            'c_phone': False,
            'c_acctbal': False,
            'c_mktsegment': False,
            'c_comment': False
        },
        'orders': {
            'o_orderstatus': False,
            'o_totalprice': False,
            'o_orderdate': False,
            'o_orderpriority': False,
            'o_clerk': False,
            'o_shippriority': False,
            'o_comment': False
        },
        'lineitem': {
            'l_quantity': False,
            'l_extendedprice': False,
            'l_discount': False,
            'l_tax': False,
            'l_returnflag': False,
            'l_linestatus': False,
            'l_shipdate': False,
            'l_commitdate': False,
            'l_receiptdate': False,
            'l_shipinstruct': False,
            'l_shipmode': False,
            'l_comment': False
        }
    }

    def __init__(self, benchmark: Benchmark = None):
        super().__init__(benchmark)
        # self._benchmark_results = self._mock_benchmark_results()
        self.reset_indexes()
        self.random_generator = random.Random(1)

    def execute_action(self, action: int) -> None:
        db_action = self.action_mapper[action]
        self._state[db_action[0]][db_action[1]] = db_action[2] == 'CREATE INDEX'

    def execute_benchmark(self) -> float:
        # return self._benchmark_results[str(self._get_mapped_state())]
        if sum(self._get_mapped_state()) == 0:
            return 1000
        return self.random_generator.randint(500, 2500)

    def reset_indexes(self) -> None:
        for table_name, cols in self._state.items():
            for col_name in cols:
                self._state[table_name][col_name] = False

    def _get_current_mapped_database(self) -> dict[str, dict[str, bool]]:
        return self._database_schema_as_dict

    def _get_mapped_state(self) -> List[bool]:
        """:return: Map database state to environment observation"""
        observation: list[bool] = []
        for table in self._state.values():
            for is_indexed in table.values():
                observation.append(int(is_indexed))
        return observation
