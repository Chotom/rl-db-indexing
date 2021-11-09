import glob
import os
import shutil
import subprocess
from pathlib import Path

from db_env.tpch.config import MAX_REFRESH_FILE_INDEX, DB_GENERATOR_TOOL, DB_DATA_DIR, SCALE_FACTOR, DB_REFRESH_DIR, \
    DB_QUERIES_DIR
from shared_utils.consts import DB_NAME
from shared_utils.utils import get_connection
from shared_utils.utils import create_logger


class TpchGenerator:
    """
    A class for generating, loading, resetting data for database
    """

    def __init__(self):
        self._log = create_logger('database_generator')

    def generate_data(self):
        """Generate database input"""
        self._log.info(f'Generating data with dbgen in {DB_GENERATOR_TOOL}/dbgen dir')

        # call dbgen with scale factor
        subprocess.run([f'{DB_GENERATOR_TOOL}/dbgen', '-vf', '-s', f'{SCALE_FACTOR}'],
                       cwd=DB_GENERATOR_TOOL)

        # create folder for data if not exist
        Path(DB_DATA_DIR).mkdir(parents=True, exist_ok=True)

        # move generated data to data folder
        for file in glob.glob(f'{DB_GENERATOR_TOOL}/*.tbl'):
            shutil.move(file, f'{DB_DATA_DIR}/{os.path.basename(file)}')

    def reset_db(self):
        """Drop database, create new database"""
        connection, cursor = get_connection(self._log, True, False)

        try:
            # Drop old database
            sql = f'DROP DATABASE IF EXISTS `{DB_NAME}`'
            cursor.execute(sql)

            # Create new database
            sql = f'CREATE DATABASE `{DB_NAME}`'
            cursor.execute(sql)

            # allow loading files from local input files
            sql = 'SET GLOBAL local_infile=1'
            cursor.execute(sql)
        except Exception as e:
            self._log.error(f'Exception occurred: {e}')
            raise

        connection.close()
        self._log.info("Database reset successfully")

    def load_db(self):
        """Create tables, load generated data, set indexes and relations"""
        connection, cursor = get_connection(self._log, True)

        try:
            # Create tables in database
            self._log.info('Creating tables in database...')

            # Load file 'dss.ddl' to database
            with open(f'{DB_GENERATOR_TOOL}/dss.ddl') as ddl_file:
                sql = ddl_file.read()
                for _ in cursor.execute(sql, multi=True):
                    pass

            # Load '*.tbl' files to database
            self._log.info('Loading data to database...')

            # temporarily disable foreign key checking
            sql = 'SET foreign_key_checks=0'
            cursor.execute(sql)

            # for each table, which is represented by '*.tbl' file
            for tbl_file in glob.glob(f'{DB_DATA_DIR}/*.tbl'):
                # extract table name from filepath
                table_name = Path(tbl_file).stem
                self._log.info(f'Loading table \'{table_name}\'')

                # load data from tbl_file to database
                sql = f"LOAD DATA LOCAL INFILE '{tbl_file}' " \
                      f"INTO TABLE {table_name} " \
                      f"FIELDS TERMINATED BY '|' " \
                      f"LINES TERMINATED BY '|\\n'"
                cursor.execute(sql)

            # re-enable foreign key checking
            sql = 'SET foreign_key_checks=1'
            cursor.execute(sql)

            self._log.info('Creating indexes and relations in database...')
            # Load file 'dss.ri' to database
            with open(f'{DB_GENERATOR_TOOL}/dss.ri') as ri_file:
                for _ in cursor.execute(ri_file.read(), multi=True):
                    pass

        except Exception as e:
            self._log.error(f'Exception occurred: {e}')
            raise

        connection.close()
        self._log.info('Database created and loaded successfully.')

    def generate_refresh_data(self, updates=MAX_REFRESH_FILE_INDEX):
        """Generate refresh data for 4000 (or n) RF1/RF2 pairs: updates and deletes"""

        self._log.info('Generating refresh data with dbgen...')

        # call dbgen with scale factor and updates
        subprocess.run([f'{DB_GENERATOR_TOOL}/dbgen',
                        '-vf',
                        '-U', f'{updates}',
                        '-s', f'{SCALE_FACTOR}'],
                       cwd=DB_GENERATOR_TOOL)
        # create folder for refresh data
        Path(DB_REFRESH_DIR).mkdir(parents=True, exist_ok=True)

        # move generated updates to refresh data folder
        for file in [f for f_ in [glob.glob(f'{DB_GENERATOR_TOOL}/{type}') for _ in ('*.tbl.u*', 'delete.*')] for f in
                     f_]:
            shutil.move(file, f'{DB_REFRESH_DIR}/{os.path.basename(file)}')

    def generate_queries(self, start_seed, sets):
        """Create queries and directory for each set"""

        self._log.info('Generating queries with qgen...')

        # for each required update
        for i in range(sets):
            # create directory for each set of queries
            Path(f'{DB_QUERIES_DIR}/{i}').mkdir(parents=True, exist_ok=True)
            for j in range(1, 22 + 1):
                # create output file if not exists
                with open(f'{DB_QUERIES_DIR}/{i}/{j}.sql', 'w+') as output_file:
                    # call qgen
                    subprocess.run([f'{DB_GENERATOR_TOOL}/qgen',
                                    f'{j}',
                                    '-p', f'{i}',
                                    '-r', f'{start_seed + i}'],
                                   cwd=DB_GENERATOR_TOOL,
                                   env=dict(os.environ, DSS_QUERY=f'{DB_GENERATOR_TOOL}/queries'),
                                   stdout=output_file)


if __name__ == '__main__':
    generator = TpchGenerator()
    generator.reset_db()
    generator.generate_data()
    generator.load_db()
    generator.generate_refresh_data()
