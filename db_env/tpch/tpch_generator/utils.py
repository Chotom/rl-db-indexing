import logging
import os

import mysql
from mysql.connector import MySQLConnection


def get_connection(log: logging.Logger, is_buffered: bool, connect_to_database: bool = True):
    """:return: MySql connection with cursor as tuple"""

    log.info('Trying to connect to database...')

    db_config = {}
    try:
        db_config['user'] = os.environ['USER']
        db_config['password'] = os.environ['MYSQL_ROOT_PASSWORD']
        db_config['host'] = os.environ['MYSQL_HOST']
        db_config['port'] = os.environ['MYSQL_PORT']
        if (connect_to_database):
            db_config['database'] = os.environ['MYSQL_DB']
    except KeyError as e:
        log.error(f'DB config required values not found in .env file: {e}')

    try:
        connection = mysql.connector.MySQLConnection()
        connection.connect(**db_config, allow_local_infile=True)
        connection.set_allow_local_infile_in_path("/")
        cursor = connection.cursor(buffered=is_buffered)
    except mysql.connector.Error as e:
        log.error(f'Cannot connect to database: {e}')
        raise
    log.info('Database connected successful.')
    return connection, cursor