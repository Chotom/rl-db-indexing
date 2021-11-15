from db_env.tpch.TpchBenchmark import TpchBenchmark

if __name__ == '__main__':
    benchmark = TpchBenchmark()
    print(benchmark.execute())