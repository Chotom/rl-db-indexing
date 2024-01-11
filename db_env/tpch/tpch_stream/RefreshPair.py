import datetime
from typing import Iterator, Tuple, List

import numpy as np
import pandas as pd
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursorBuffered

from db_env.tpch.config import DB_REFRESH_DIR
from db_env.tpch.tpch_stream.consts import LINEITEM_QUOTE_INDEX_LIST, ORDERS_QUOTE_INDEX_LIST, VALUE_SEP
from shared_utils.utils import create_logger


class RefreshPair:
    __insert_queries_iter: Iterator[str]

    def __init__(self, logger_name: str, run_number: int, connection: MySQLConnection, cursor: MySQLCursorBuffered):
        self._log = create_logger(logger_name)
        self._connection = connection
        self._cursor = cursor
        self.__run_number = run_number
        self.__rf1_time = datetime.timedelta(0)
        self.__rf2_time = datetime.timedelta(0)
        self._df_measures = pd.DataFrame(columns=['name', 'time'], dtype=np.dtype(str, np.timedelta64))
        self._df_measures.set_index('name', inplace=True)

    def load_data(self):
        self._log.info('Load refresh queries...')

        insert_queries = []

        # Load insert queries from files
        with open(f'{DB_REFRESH_DIR}/orders.tbl.u{self.__run_number}', 'r') as orders_file, \
                open(f'{DB_REFRESH_DIR}/lineitem.tbl.u{self.__run_number}', 'r') as lineitem_file:
            try:
                # read first lineitem query
                lineitem_row = next(lineitem_file)
                lineitem_id, lineitem_query = self._data_row_to_query(lineitem_row, 'lineitem',
                                                                      LINEITEM_QUOTE_INDEX_LIST)
            except StopIteration:
                raise Exception("Lineitem update file is empty.")

            for orders_row in orders_file:
                # read orders query
                orders_id, orders_query = self._data_row_to_query(orders_row, 'orders', ORDERS_QUOTE_INDEX_LIST)
                insert_queries.append(orders_query)

                # read next lineitem query if current orders query has lineitem children
                while orders_id == lineitem_id and (lineitem_row := next(lineitem_file, None)) is not None:
                    # add lineitem
                    insert_queries[-1] += lineitem_query
                    lineitem_id, lineitem_query = self._data_row_to_query(lineitem_row, 'lineitem',
                                                                          LINEITEM_QUOTE_INDEX_LIST)

        # save queries
        self.__insert_queries_iter = iter(insert_queries)

        # load delete queries
        with open(f'{DB_REFRESH_DIR}/delete.{self.__run_number}', 'r') as deletes_file:
            delete_queries = deletes_file.readlines()

            for i, delete_row in enumerate(delete_queries):
                delete_queries[i] = self._delete_row_to_query(delete_row)

        # save queries
        self.__delete_queries_iter = iter(delete_queries)

        self._log.info('Refresh queries loaded successfully...')

    def execute_pair(self):
        self._log.info(f'Run refresh pair {self.__run_number}...')

        self.execute_refresh_function1()
        self.execute_refresh_function2()

        self._log.info(
            f'Execution of refresh pair {self.__run_number} ended successfully. Measured time: {self.__rf1_time + self.__rf2_time}')

    def execute_refresh_function1(self):
        self._log.info('Run refresh function 1...')

        # Execute insert queries
        for query in self.__insert_queries_iter:
            # Insert new order into `orders` and its items into `lineitem`
            cursors_generator = self._cursor.execute(query, multi=True)

            # Measure time for transaction
            start = datetime.datetime.now()

            # for _ in cursors_generator: pass    # iterate over generated cursors to execute them and get the results
            cursors = [cur for cur in cursors_generator]
            self._connection.commit()

            time_delta = datetime.datetime.now() - start
            self.__rf1_time += time_delta

            # Print additional information
            self._log.debug(f'Time for {query} query: {time_delta}')

        self._df_measures = self._df_measures.append({'name': f'RF1_{self.__run_number}', 'time': self.__rf1_time},
                                                     ignore_index=True)
        self._log.info(f'Execution of refresh function 1 ended successfully. Measured time: {self.__rf1_time}')

    def execute_refresh_function2(self):
        self._log.info('Run refresh function 2...')

        # Execute delete queries
        for query in self.__delete_queries_iter:
            # Delete order from `orders` and its items from `lineitem`
            cursors_generator = self._cursor.execute(query, multi=True)

            # Measure time for transaction
            start = datetime.datetime.now()

            # for _ in cursors_generator: pass    # iterate over generated cursors to execute them and get the results
            cursors = [cur for cur in cursors_generator]
            self._connection.commit()

            time_delta = datetime.datetime.now() - start
            self.__rf2_time += time_delta

            # Print additional information
            self._log.debug(f'Time for {query} query: {time_delta}')

        self._df_measures = self._df_measures.append({'name': f'RF2_{self.__run_number}', 'time': self.__rf2_time},
                                                     ignore_index=True)
        self._log.info(f'Execution of refresh function 2 ended successfully. Measured time: {self.__rf2_time}')

    @property
    def df_measures(self) -> pd.DataFrame:
        """:return: dataframe with measured queries and total_time of execution"""
        return self._df_measures.set_index('name')

    def _data_row_to_query(self, row: str, table_name: str, quoted_values_indexes: List[int]) -> Tuple[int, str]:
        """
        Convert string data into mysql insert query.

        :param row: data separated by '|' in string for query to insert
        :param table_name: table name to insert values
        :param quoted_values_indexes: indexes of varchar columns in table
        :return: tuple of record id and Mysql query to execute
        """

        # Remove last '|' or '\n' character and split into values
        values = row.rstrip('\n|').split('|')

        # Surround varchar values with quotes
        for index in quoted_values_indexes:
            values[index] = f"'{values[index]}'"

        return int(values[0]), f'INSERT INTO `{table_name}` VALUES ({VALUE_SEP.join(values)});'

    def _delete_row_to_query(self, delete_row: str) -> str:
        id = delete_row.rstrip('\n|')
        # return f'DELETE FROM `orders`, `lineitem`' \
        #        f'USING `orders` INNER JOIN `lineitem` ON `orders`.`o_orderkey` = `l_orderkey`' \
        #        f'WHERE O_ORDERKEY = {id};'
        return f'DELETE FROM lineitem WHERE l_orderkey = {id}; DELETE FROM orders WHERE o_orderkey = {id};'
