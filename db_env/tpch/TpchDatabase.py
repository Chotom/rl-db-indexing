import logging
import os

import dotenv
import mysql
from mysql.connector import MySQLConnection

from db_env.Benchmark import Benchmark
from db_env.Database import Database


class TpchDatabase(Database):
    _dotenv_path = './.env'

    def __init__(self, benchmark: Benchmark):
        super().__init__(benchmark)
        dotenv.load_dotenv(self._dotenv_path)

    def execute_action(self, action: int) -> None:
        pass

    def execute_benchmark(self) -> float:
        pass

    def reset_indexes(self) -> None:
        pass

    @staticmethod
    def get_connection(log: logging.Logger, is_buffered: bool):
        """:return: MySql connection with cursor as tuple"""

        log.info('Trying to connect to database...')

        db_config = {}
        try:
            db_config['user'] = os.environ['USER']
            db_config['password'] = os.environ['MYSQL_ROOT_PASSWORD']
            db_config['host'] = os.environ['MYSQL_HOST']
            db_config['port'] = os.environ['MYSQL_PORT']
            db_config['database'] = os.environ['MYSQL_DB']
        except KeyError as e:
            log.error(f'DB config required values not found in .env file: {e}')

        try:
            connection = MySQLConnection()
            connection.connect(**db_config, allow_local_infile=True)
            connection.set_allow_local_infile_in_path("/")
            cursor = connection.cursor(buffered=is_buffered)
        except mysql.connector.Error as e:
            log.error(f'Cannot connect to database: {e}')
            raise
        log.info('Database connected successful.')
        return connection, cursor

    def _get_current_mapped_database(self) -> dict[str, dict[str, bool]]:
        pass