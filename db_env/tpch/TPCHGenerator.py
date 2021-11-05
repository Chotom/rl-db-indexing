import glob
import os
import shutil
import subprocess
from pathlib import Path
from mysql.connector import MySQLConnection

from db_env.tpch.tpch_generator.consts import *
from db_env.tpch.tpch_generator.utils import get_connection
from shared_utils.utils import create_logger


class TPCHGenerator:
    """
    A class for generating, loading, resetting data for database
    """

    def __init__(self):
        self._log = create_logger('database_generator')

    def generate_data(self):
        self._log.info('Generating data with dbgen...')
        """Generate database input"""
        # generate database bulk load
        # call dbgen with scale factor
        subprocess.run([f'{DBGEN_DIR}/dbgen',
                        '-vf',
                        '-s', f'{SCALE_FACTOR}'],
                       cwd=DBGEN_DIR)
        # create folder for data if not exist
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
        # move generated data to data folder
        for file in glob.glob(f'{DBGEN_DIR}/*.tbl'):
            shutil.move(file, f'{DATA_DIR}/{os.path.basename(file)}')

    def reset_db(self):
        """Drop database, create new database"""
        global connection

        try:
            connection, cursor = get_connection(self._log, True, False)
            cursor, connection = connection.cursor(buffered=True)

            # Drop old database
            sql = f'DROP DATABASE IF EXISTS `{os.environ["MYSQL_DB"]}`'
            cursor.execute(sql)

            # Create new database
            sql = f'CREATE DATABASE `{os.environ["MYSQL_DB"]}`'
            cursor.execute(sql)

            # allow loading files from local input files
            sql = 'SET GLOBAL local_infile=1'
            cursor.execute(sql)
        except Exception as e:
            self._log.error(f'Exeception occured: {e}')
            return
        finally:
            connection.close()
        self._log.info("Database reset successfully")

    def load_db(self):
        """Create tables, load generated data, set indexes and relations"""
        global connection

        try:
            connection, cursor = get_connection(self._log, True)

            # Create tables in database
            self._log.info('Creating tables in database...')
            # Load file 'dss.ddl' to database
            with open(f'{DBGEN_DIR}/dss.ddl') as ddl_file:
                sql = ddl_file.read()
                for _ in cursor.execute(sql, multi=True):
                    pass

            # Load '*.tbl' files to database
            self._log.info('Loading data to database...')
            # temporarily disable foreign key checking
            sql = 'SET foreign_key_checks=0'
            cursor.execute(sql)
            # for each table, which is represented by '*.tbl' file
            for tbl_file in glob.glob(f'{DATA_DIR}/*.tbl'):
                # extract table name from filepath
                table_name = Path(tbl_file).stem

                self._log.info(f'Loading table \'{table_name}\'')

                # load data from tbl_file to database
                sql = f"LOAD DATA LOCAL INFILE '{tbl_file}'" \
                      f"INTO TABLE {table_name}" \
                      f"FIELDS TERMINATED BY '|'" \
                      f"LINES TERMINATED BY '|\\n'"
                cursor.execute(sql)
            # re-enable foreign key checking
            sql = 'SET foreign_key_checks=1'
            cursor.execute(sql)

            # Create indexes and relations in database
            self._log.info('Creating indexes and relations in database...')
            # Load file 'dss.ri' to database
            with open(f'{DBGEN_DIR}/dss.ri') as ri_file:
                for _ in cursor.execute(ri_file.read(), multi=True):
                    pass

        except Exception as e:
            self._log.error(f'Exeception occured: {e}')
            return
        finally:
            connection.close()
        self._log.info('Database created and loaded successfully.')

    def generate_refresh_data(self, updates=MAX_REFRESH_FILE_INDEX):
        """Generate refresh data for 4000 (or n) RF1/RF2 pairs: updates and deletes"""

        self._log.info('Generating refresh data with dbgen...')

        # call dbgen with scale factor and updates
        subprocess.run([f'{DBGEN_DIR}/dbgen',
                        '-vf',
                        '-U', f'{updates}',
                        '-s', f'{SCALE_FACTOR}'],
                       cwd=DBGEN_DIR)
        # create folder for refresh data
        Path(REFRESH_DATA_DIR).mkdir(parents=True, exist_ok=True)

        # move generated updates to refresh data folder
        for file in [f for f_ in [glob.glob(f'{DBGEN_DIR}/{type}') for _ in ('*.tbl.u*', 'delete.*')] for f in f_]:
            shutil.move(file, f'{REFRESH_DATA_DIR}/{os.path.basename(file)}')

    def generate_queries(self, start_seed, sets):
        """Create queries and directory for each set"""

        self._log.info('Generating queries with qgen...')

        # for each required update
        for i in range(sets):
            # create directory for each set of queries
            Path(f'{QUERIES_DIR}/{i}').mkdir(parents=True, exist_ok=True)
            for j in range(1, 22 + 1):
                # create output file if not exists
                with open(f'{QUERIES_DIR}/{i}/{j}.sql', 'w+') as output_file:
                    # call qgen
                    subprocess.run([f'{DBGEN_DIR}/qgen',
                                    f'{j}',
                                    '-p', f'{i}',
                                    '-r', f'{start_seed + i}'],
                                   cwd=DBGEN_DIR,
                                   env=dict(os.environ, DSS_QUERY=f'{DBGEN_DIR}/queries'),
                                   stdout=output_file)
