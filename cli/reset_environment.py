from db_env.tpch.TpchGenerator import TpchGenerator

if __name__ == '__main__':
    generator = TpchGenerator()
    generator.reset_db()
    generator.load_db()