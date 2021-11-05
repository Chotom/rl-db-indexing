import os
from threading import Thread

import dotenv
import pandas as pd
import numpy as np

from db_env.Benchmark import Benchmark
from db_env.tpch.TpchDatabase import TpchDatabase
from db_env.tpch.tpch_stream.QueryStream import QueryStream
from db_env.tpch.tpch_stream.RefreshPair import RefreshPair
from db_env.tpch.tpch_stream.RefreshStream import RefreshStream
from db_env.tpch.tpch_stream.Stream import Stream
from shared_utils.logger import create_logger


class TpchBenchmark(Benchmark):
    def __init__(self):
        self._log = create_logger('tpch_benchmark')
        self._load_env()
        self._generate_data()

    def prepare_queries(self) -> None:
        pass

    def execute(self) -> float:
        power_size = self._run_power_test()
        self._inc_refresh_file_index()

        throughput_size = self._run_throughput_test()
        self._inc_refresh_file_index(self._stream_count)

        # todo: save db.env file (start_seed, rf_index_file)

        return (power_size * throughput_size) ** (1 / 2)

    def _inc_refresh_file_index(self, number: int = 1):
        self._refresh_file_index = (self._refresh_file_index + number) % self._max_rf_file_id

    def _generate_data(self) -> None:
        # todo: Add data generating here
        pass

    def _load_env(self):
        try:
            self._stream_count = os.environ['STREAM_COUNT']
        except KeyError as e:
            self._log.error(f'STREAM_COUNT not found in db.env file: {e}')

        try:
            self._refresh_file_index = os.environ['RF_FILE_ID']
        except KeyError as e:
            self._log.error(f'RF_FILE_ID not found in db.env file: {e}')

        try:
            self._max_rf_file_id = os.environ['MAX_RF_FILE_ID']
        except KeyError as e:
            self._log.error(f'MAX_RF_FILE_ID not found in db.env file: {e}')

        try:
            self._scale_factor = float(os.environ['SCALE_FACTOR'])
        except KeyError as e:
            self._log.error(f'SCALE_FACTOR not found in db.env file: {e}')

    def _run_power_test(self) -> float:
        """
        Execute refresh pair 1, query stream and refresh pair 2 in sequence to
        measure database benchmark for single user and saves measurements.

        :return: calculated power size measure
        """

        refresh_pair, query_stream = self._prepare_power_test()
        return self._execute_power_test(refresh_pair, query_stream)

    def _prepare_power_test(self) -> (RefreshPair, QueryStream):
        connection, cursor = TpchDatabase.get_connection(self._log, True)
        refresh_pair = RefreshPair('refresh_pair_powertest', self._refresh_file_index, connection, cursor)
        query_stream = QueryStream('query_stream_powertest', 0, connection, cursor)
        refresh_pair.load_data()
        query_stream.load_data()

        return refresh_pair, query_stream

    def _execute_power_test(self, refresh_pair: RefreshPair, query_stream: QueryStream) -> float:
        refresh_pair.execute_refresh_function1()
        query_stream.execute_stream()
        refresh_pair.execute_refresh_function2()

        return self._calculate_power_test_result(refresh_pair, query_stream)

    def _calculate_power_test_result(self, refresh_pair: RefreshPair, query_stream: QueryStream) -> float:
        power_test_results = query_stream.df_measures.append(refresh_pair.df_measures)
        geometric_mean = np.prod(power_test_results['time'].apply(lambda x: x.total_seconds())) ** (1 / 24)
        power_size = 3600 * self._scale_factor / geometric_mean

        return power_size

    def _run_throughput_test(self) -> float:
        """
        Execute refresh stream and given number of query streams in parallel threads and
        measure database benchmark for single user and saves measurements.

        :return: calculated throughput size measure
        """

        streams, processes = self._prepare_throughput_test()
        return self._execute_throughput_test(streams, processes)

    def _prepare_throughput_test(self) -> (list[Stream], list[Thread]):
        processes = []
        streams = [RefreshStream('refresh_stream', self._stream_count, self._refresh_file_index)]
        for i in range(self._stream_count):
            streams.append(QueryStream(f'query_stream_{i + 1}', i + 1))

        for stream in streams:
            stream.load_data()
            processes.append(Thread(target=stream.execute_stream))

        return streams, processes

    def _execute_throughput_test(self, streams: list[Stream], processes: list[Thread]) -> float:
        # Execute streams in parallel threads
        for execute_stream_process in processes:
            execute_stream_process.start()

        # Wait for all processes to end
        for proc in processes:
            proc.join()

        return self._calculate_throughput_test_result(streams)

    def _calculate_throughput_test_result(self, streams: list[Stream]):
        total_time = max(stream.df_measures['time'].sum() for stream in streams)
        throughput_size = (len(streams) - 1) * 22 * 3600 * self._scale_factor / total_time.total_seconds()

        return throughput_size
