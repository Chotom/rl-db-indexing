import datetime
from typing import Iterator

from db_env.tpch.config import MAX_REFRESH_FILE_INDEX
from db_env.tpch.tpch_stream.RefreshPair import RefreshPair
from db_env.tpch.tpch_stream.Stream import Stream


class RefreshStream(Stream):
    __orders_queries_iter: Iterator[str]
    __lineitem_queries_iter: Iterator[str]

    def __init__(self, logger_name: str, stream_count: int, refresh_file_start_index: int):
        super().__init__(logger_name, False)
        self.__S = stream_count
        self.__rf1_time = datetime.timedelta(0)
        self.__rf2_time = datetime.timedelta(0)
        self.__file_start_index = refresh_file_start_index

        self.__refresh_pairs = []

        for i in range(stream_count):
            # modulo, but not zero
            file_index = (self.__file_start_index + i - 1) % MAX_REFRESH_FILE_INDEX + 1
            self.__refresh_pairs.append(
                RefreshPair(f'refresh_pair_{i + 1}', file_index, self._connection, self._cursor)
            )

    def load_data(self):
        self._log.info('Load queries...')

        for refresh_pair in self.__refresh_pairs:
            refresh_pair.load_data()

        self._log.info('Queries loaded successfully...')

    def execute_stream(self):
        self._log.info('Run refresh stream...')

        for i, refresh_pair in enumerate(self.__refresh_pairs):
            refresh_pair.execute_pair()
            self._df_measures = self._df_measures.append({'name': f'RF1_{i}', 'time': refresh_pair.df_measures.at[f'RF1_{i + self.__file_start_index }', 'time']}, ignore_index=True)
            self._df_measures = self._df_measures.append({'name': f'RF2_{i}', 'time': refresh_pair.df_measures.at[f'RF2_{i + self.__file_start_index }', 'time']}, ignore_index=True)

        self._log.info(f'Execution of refresh stream ended successful. Measured time: {self._df_measures["time"].sum()}')
