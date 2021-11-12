from typing import Dict

from db_env.Database import Database
from db_env.tpch.TpchBenchmark import TpchBenchmark
from db_env.tpch.TpchGenerator import TpchGenerator
from shared_utils.utils import get_connection, create_logger
from db_env.tpch.config import TPCH_MUTABLE_COLUMNS


class TpchDatabase(Database):
    def __init__(self):
        self._log = create_logger('tpch_database')
        super(TpchDatabase, self).__init__(TpchBenchmark())

    def execute_action(self, action: int) -> None:
        connection, cursor = get_connection(self._log, True)

        table_name, key_name, action_name = self.action_mapper[action]
        index_name = f'{table_name}_{key_name}_index'

        if action_name == "DROP INDEX":
            self._log.info(f"Executing action - drop index '{index_name}'")
            sql = f'DROP INDEX {index_name} ON {table_name}'
        else:
            self._log.info(f"Executing action - create index '{index_name}'")
            sql = f'CREATE INDEX {index_name} ON {table_name} ({key_name})'

        cursor.execute(sql)
        self._state[table_name][key_name] = action_name != "DROP INDEX"

        cursor.close()
        connection.close()

    def execute_benchmark(self) -> float:
        return self._benchmark.execute()

    def reset_indexes(self) -> None:
        connection, cursor = get_connection(self._log, True)

        self._log.info('Resetting indexes')

        for table_name, key_name in TPCH_MUTABLE_COLUMNS:
            index_name = f'{table_name}_{key_name}_index'

            # check if index exists
            sql = f"SHOW INDEX FROM {table_name} WHERE KEY_NAME = '{index_name}'"
            cursor.execute(sql)

            # drop if exists
            if len(cursor.fetchall()) > 0:
                self._log.info(f"Dropping index '{index_name}'")
                sql = f'DROP INDEX {index_name} ON {table_name}'
                cursor.execute(sql)
            connection.commit()

        cursor.close()
        connection.close()

        self._state = self._get_current_mapped_database()

    def _get_current_mapped_database(self) -> Dict[str, Dict[str, bool]]:
        connection, cursor = get_connection(self._log, True)

        self._log.info('Mapping database state')

        state = dict()
        for table_name, key_name in TPCH_MUTABLE_COLUMNS:
            state[table_name] = dict()

        for table_name, key_name in TPCH_MUTABLE_COLUMNS:
            index_name = f'{table_name}_{key_name}_index'
            sql = f"SHOW INDEX FROM {table_name} WHERE KEY_NAME = '{index_name}'"
            cursor.execute(sql)

            state[table_name][key_name] = (len(cursor.fetchall()) > 0)

        cursor.close()
        connection.close()

        return state