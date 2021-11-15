import logging
import sys

import mysql
from mysql.connector import MySQLConnection

from shared_utils.consts import LOG_LEVEL, DB_CONFIG, DB_NAME


def create_logger(name: str) -> logging.Logger:
    """
    Create logger for given name

    :param name: name of logger
    :return: logger
    """

    log_format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    if not len(logger.handlers):
        logger.addHandler(console_handler)
    return logger


def get_connection(log: logging.Logger, is_buffered: bool, choose_database: bool = True):
    """:return: MySql connection with cursor as tuple"""
    if choose_database:
        DB_CONFIG['database'] = DB_NAME

    log.info('Trying to connect to database...')
    try:
        connection = MySQLConnection()
        connection.connect(**DB_CONFIG, allow_local_infile=True)
        cursor = connection.cursor(buffered=is_buffered)
    except mysql.connector.Error as e:
        log.error(f'Cannot connect to database: {e}')
        raise
    log.info('Database connected successful.')
    return connection, cursor
