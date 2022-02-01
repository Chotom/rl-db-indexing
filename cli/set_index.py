from db_env.tpch.TpchBenchmark import TpchBenchmark
from db_env.tpch.config import TPCH_MUTABLE_COLUMNS
from shared_utils.utils import get_connection, create_logger

_log = create_logger('cli')


def _get_index_name(table_name, key_name):
    return f'{table_name}_{key_name}_index'


def _index_exist(cursor, table_name: str, key_name: str) -> bool:
    index_name = _get_index_name(table_name, key_name)

    sql = f"SHOW INDEX FROM {table_name} WHERE KEY_NAME = '{index_name}'"
    cursor.execute(sql)

    return len(cursor.fetchall()) > 0


def _drop_index(cursor, table_name: str, key_name: str):
    index_name = _get_index_name(table_name, key_name)

    _log.info(f"Dropping index '{index_name}'")
    sql = f'DROP INDEX {index_name} ON {table_name}'
    cursor.execute(sql)


def _create_index(cursor, table_name: str, key_name: str):
    index_name = _get_index_name(table_name, key_name)

    _log.info(f"Creating index '{index_name}'")
    sql = f'CREATE INDEX {index_name} ON {table_name} ({key_name})'
    cursor.execute(sql)


if __name__ == '__main__':
    state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    connection, cursor = get_connection(_log, True)

    for set_index, (table_name, key_name) in zip(state, TPCH_MUTABLE_COLUMNS):
        index_exists = _index_exist(cursor, table_name, key_name)

        if set_index and not index_exists:
            _create_index(cursor, table_name, key_name)
            connection.commit()
            index_exists = True
        elif not set_index and index_exists:
            _drop_index(cursor, table_name, key_name)
            connection.commit()
            index_exists = False

    benchmark = TpchBenchmark()
    _log.info(benchmark.execute())
