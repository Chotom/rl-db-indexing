from db_env.tpch.TpchDatabase import TpchDatabase

if __name__ == '__main__':
    database = TpchDatabase()
    database.reset_indexes()