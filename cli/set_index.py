import argparse

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


def process_index_config(index_config):
    if len(index_config) != 45:
        raise ValueError("Error: The index_config string must be exactly 45 characters long.")

    for char in index_config:
        if char != '0' and char != '1':
            raise ValueError("Error: The index_config string must consist only of 0s and 1s.")

    index_array = [int(char) for char in index_config]
    return index_array


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set the index configuration based on a string of 0s and 1s",
                                     epilog=f"Example:\n"
                                            f"python set_index.py 1{'0' * (len(TPCH_MUTABLE_COLUMNS) - 1)}\n"
                                            f"This will switch database to state with only one index created (on table "
                                            f"'{TPCH_MUTABLE_COLUMNS[0][0]}' on column '{TPCH_MUTABLE_COLUMNS[0][1]}')",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('index_config', type=str,
                        help=f"String of 0s and 1s representing the presence (1) or absence (0) of an index in each of "
                             f"the {len(TPCH_MUTABLE_COLUMNS)} columns. Must be exactly {len(TPCH_MUTABLE_COLUMNS)} "
                             f"characters long. Tables and columns come in the following order: "
                             f"{str(TPCH_MUTABLE_COLUMNS)[1:-1]}.")
    args = parser.parse_args()


    try:
        index_array = process_input(args.index_config)
    except ValueError as e:
        print(e)
        parser.print_help()
        exit(1)

    connection, cursor = get_connection(_log, True)

    for set_index, (table_name, key_name) in zip(index_array, TPCH_MUTABLE_COLUMNS):
        index_exists = _index_exist(cursor, table_name, key_name)

        if set_index and not index_exists:
            _create_index(cursor, table_name, key_name)
            connection.commit()
        elif not set_index and index_exists:
            _drop_index(cursor, table_name, key_name)
            connection.commit()
