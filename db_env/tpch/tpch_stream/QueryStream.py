import datetime
from typing import Optional, Generator, Any, List

import pandas as pd
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from db_env.tpch.config import DB_QUERIES_DIR
from db_env.tpch.tpch_stream.Stream import Stream
from db_env.tpch.tpch_stream.consts import QUERY_ORDER


class QueryStream(Stream):

    def __init__(self, logger_name: str, stream_number: int, conn: MySQLConnection = None, cursor: MySQLCursor = None):
        super().__init__(logger_name, True, conn, cursor)
        self._stream_number = stream_number
        self._query_order: List[int] = QUERY_ORDER[stream_number]
        self._query_iter: List[Optional[Generator[MySQLCursor, Any, None]]] = []

    def load_data(self):
        self._log.info('Load queries...')

        # Load queries from files to memory
        for i in range(0, 22):
            with open(f'{DB_QUERIES_DIR}/{self._stream_number}/{i + 1}.sql') as query_file:
                query = query_file.read()
                self._query_iter.append(self._cursor.execute(query, multi=True))
        self._log.info('Queries loaded successfully...')

    def execute_stream(self):
        self._log.info('Run query stream...')

        # Execute all queries
        for i in range(0, 22):
            # Measure time for query
            start = datetime.datetime.now()

            # Iterate over generated cursors to execute them and get the results
            cursors = [cur for cur in self._query_iter[i]]  # for _ in cursors_generator: pass

            time_delta = datetime.datetime.now() - start
            self._df_measures: pd.DataFrame = (
                self._df_measures.append({'name': f'Q{self._query_order[i]}', 'time': time_delta}, ignore_index=True)
            )

            # Print additional information
            self._log.info(f'Time for query {self._query_order[i]}: {time_delta}')
            for cur in cursors:
                self._log.debug(f'Cursor:\n {cur}')
                if cur.with_rows:
                    self._log.debug(f'Results:\n {cur.fetchall()}')
        self._log.info(f'Execution of query stream ended successfully. Measured time: {self._df_measures["time"].sum()}')
