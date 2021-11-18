from typing import Dict

from db_env.Database import Database
from db_env.tpch.TpchBenchmark import TpchBenchmark
from shared_utils.utils import get_connection, create_logger
from db_env.tpch.config import TPCH_MUTABLE_COLUMNS


class TpchDatabase(Database):
    def __init__(self):
        self._log = create_logger('tpch_database')
        super(TpchDatabase, self).__init__(TpchBenchmark())

    def execute_action(self, action: int) -> None:
        connection, cursor = get_connection(self._log, True)

        table_name, key_name, action_name = self.action_mapper[action]

        self._log.info(f"Executing action - {action_name} '{self._get_index_name(table_name, key_name)}'")
        if action_name == "DROP INDEX":
            self._drop_index(cursor, table_name, key_name)
            self._state[table_name][key_name] = False
        else:
            self._create_index(cursor, table_name, key_name)
            self._state[table_name][key_name] = True

        cursor.close()
        connection.close()

    def execute_benchmark(self) -> float:
        return self._benchmark.execute()

    def reset_indexes(self) -> None:
        connection, cursor = get_connection(self._log, True)

        self._log.info('Resetting indexes')

        for table_name, key_name in TPCH_MUTABLE_COLUMNS:
            if self._index_exist(cursor, table_name, key_name):
                self._drop_index(cursor, table_name, key_name)
                connection.commit()
            self._state[table_name][key_name] = False

        cursor.close()
        connection.close()

    def _get_current_mapped_database(self) -> Dict[str, Dict[str, bool]]:
        connection, cursor = get_connection(self._log, True)

        self._log.info('Mapping database state')

        state = {table_name: dict() for table_name, _ in TPCH_MUTABLE_COLUMNS}
        for table_name, key_name in TPCH_MUTABLE_COLUMNS:
            state[table_name][key_name] = self._index_exist(cursor, table_name, key_name)

        cursor.close()
        connection.close()

        return state

    def _get_index_name(sefl, table_name, key_name):
        return f'{table_name}_{key_name}_index'

    def _index_exist(self, cursor, table_name: str, key_name: str) -> bool:
        index_name = self._get_index_name(table_name, key_name)

        sql = f"SHOW INDEX FROM {table_name} WHERE KEY_NAME = '{index_name}'"
        cursor.execute(sql)

        return len(cursor.fetchall()) > 0

    def _drop_index(self, cursor, table_name: str, key_name: str):
        index_name = self._get_index_name(table_name, key_name)

        self._log.info(f"Dropping index '{index_name}'")
        sql = f'DROP INDEX {index_name} ON {table_name}'
        cursor.execute(sql)

    def _create_index(self, cursor, table_name: str, key_name: str):
        index_name = self._get_index_name(table_name, key_name)

        self._log.info(f"Creating index '{index_name}'")
        sql = f'CREATE INDEX {index_name} ON {table_name} ({key_name})'
        cursor.execute(sql)