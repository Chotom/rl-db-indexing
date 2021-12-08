from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from shared_utils.utils import create_logger, get_connection


class Stream(ABC):

    def __init__(self, logger_name: str, is_buffered: bool, conn: MySQLConnection = None, cursor: MySQLCursor = None):
        self._log = create_logger(logger_name)
        self._df_measures = pd.DataFrame(columns=['name', 'time'], dtype=np.dtype(str, np.timedelta64))
        self.__set_session(is_buffered, conn, cursor)

    @abstractmethod
    def load_data(self):
        """Prepare data and queries to be executed in database."""
        return NotImplemented

    @abstractmethod
    def execute_stream(self):
        """Execute queries in database and measure benchmark."""
        return NotImplemented

    @property
    def df_measures(self) -> pd.DataFrame:
        """:return: dataframe with measured time execution of queries."""
        return self._df_measures.set_index('name')

    @df_measures.setter
    def df_measures(self, value: pd.DataFrame):
        """Set dataframe with measures"""
        self._df_measures = value.reset_index()

    def __set_session(self, is_buffered: bool, conn: MySQLConnection, cursor: MySQLCursor):
        if conn is not None and cursor is not None:
            self._connection, self._cursor = conn, cursor
        elif conn is None and cursor is None:
            self._connection, self._cursor = get_connection(self._log, is_buffered)
        else:
            self._log.error('Database connection or cursor is not defined. Error creating stream object: missing arg.')
            raise

    def __del__(self):
        self._cursor.reset()
        self._connection.close()
