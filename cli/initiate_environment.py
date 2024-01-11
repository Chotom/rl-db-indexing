from db_env.tpch.TpchGenerator import TpchGenerator

if __name__ == '__main__':
    generator = TpchGenerator()
    generator.reset_db()
    generator.generate_data()
    generator.load_db()
    # generator.generate_refresh_data()
    generator.generate_fixed_refresh_data()
