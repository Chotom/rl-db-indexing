from db_env import Benchmark
from db_env.Database import Database


class MockDatabase(Database):
    """
    Simple example database class for tests with stored sample data. Does not
    connect with any database, all operations are simulated and perform results
    are already defined.

    Possible states and their benchmark results:
    - 01/23/45
    - [0,0,0]: some float
    - [0,0,1]: some float
    - [0,1,1]: some float
    - [0,1,0]: some float
    - [1,1,0]: some float
    - [1,1,1]: some float
    - [1,0,1]: some float
    - [1,0,0]: some float
    """

    _database_schema_as_dict = {
        "table1": {
            "column1": 0,
            "column2": 0
        },
        "table2": {
            "column1": 0
        }
    }

    def __init__(self, benchmark: Benchmark = None):
        super().__init__(benchmark)
        self._benchmark_results = self._mock_benchmark_results()

    def execute_action(self, action: int) -> None:
        db_action = self.action_mapper[action]
        self._state[db_action[0]][db_action[1]] = db_action[2] == 'CREATE'

    def execute_benchmark(self) -> float:
        return self._benchmark_results[hash(str(self._state))]

    def reset_indexes(self) -> None:
        for table_name, cols in self._state.items():
            for col_name in cols:
                self._state[table_name][col_name] = 0

    def _get_current_mapped_database(self) -> dict[str, dict[str, bool]]:
        return self._database_schema_as_dict

    def _mock_benchmark_results(self):
        # [0,0,0]
        results = {hash(str(self._state)): 1000.0}

        # [0,0,1]
        self.execute_action(5)
        results[hash(str(self._state))] = 1000.0

        # [0,1,1]
        self.execute_action(3)
        results[hash(str(self._state))] = 1000.0

        # [0,1,0]
        self.execute_action(4)
        results[hash(str(self._state))] = 1000.0

        # [1,1,0]
        self.execute_action(1)
        results[hash(str(self._state))] = 1000.0

        # [1,1,1]
        self.execute_action(5)
        results[hash(str(self._state))] = 1000.0

        # [1,0,1]
        self.execute_action(2)
        results[hash(str(self._state))] = 1000.0

        # [1,0,0]
        self.execute_action(4)
        results[hash(str(self._state))] = 1000.0

        # [0,0,0]
        self.execute_action(0)

        return results
