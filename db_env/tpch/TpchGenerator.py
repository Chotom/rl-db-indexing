import glob
import os
import shutil
import subprocess
from pathlib import Path

from db_env.tpch.config import MAX_REFRESH_FILE_INDEX, DB_GENERATOR_TOOL, DB_DATA_DIR, SCALE_FACTOR, DB_REFRESH_DIR, \
    DB_QUERIES_DIR, DB_REFRESH_ID
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

        # Save information that there was no refresh_pair executed on current database
        with open(DB_REFRESH_ID, 'w') as f:
            f.write("1")

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
        for file in [f for f_ in [glob.glob(f'{DB_GENERATOR_TOOL}/{file_type}')
                                  for file_type in ('*.tbl.u*', 'delete.*')] for f in f_]:
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

    def generate_fixed_refresh_data(self):
        """Generate fixed refresh data for 1998 RF1/RF2 pairs: updates and deletes"""
        self.generate_refresh_data(updates=1998)

        for i in range(1, 1000):
            delete_file = f'{DB_REFRESH_DIR}/delete.{i}'
            orders_file = f'{DB_REFRESH_DIR}/orders.tbl.u{i + 999}'
            lineitem_file = f'{DB_REFRESH_DIR}/lineitem.tbl.u{i + 999}'

            self._place_ids_from_delete_to_orders_and_lineitem(delete_file, orders_file, lineitem_file)

        for i in range(1, 1000):
            orders_file = f'{DB_REFRESH_DIR}/orders.tbl.u{i}'
            delete_file = f'{DB_REFRESH_DIR}/delete.{i + 999}'

            self._place_ids_from_orders_to_delete(orders_file, delete_file)

    def _place_ids_from_delete_to_orders_and_lineitem(self, delete_file, orders_file, lineitem_file):
        with open(delete_file, 'r') as file:
            delete_lines = file.readlines()
        delete_ids = [line.split('|')[0] for line in delete_lines]

        with open(orders_file, 'r') as file:
            orders_lines = file.readlines()
        orders_rests = [orders_line.split('|')[1:] for orders_line in orders_lines]

        assert len(delete_ids) == len(orders_rests)

        orders_new_lines = ["|".join([delete_id] + orders_rest) for delete_id, orders_rest in
                            zip(delete_ids, orders_rests)]

        with open(orders_file, 'w') as file:
            file.writelines(orders_new_lines)

        with open(lineitem_file, 'r') as file:
            lineitem_lines = file.readlines()
        delete_ids_iterator = 0
        lineitem_last_id = None
        lineitem_new_lines = []

        for lineitem_line in lineitem_lines:
            lineitem_id = lineitem_line.split('|')[0]
            lineitem_rest = lineitem_line.split('|')[1:]

            if lineitem_last_id is not None and lineitem_id != lineitem_last_id:
                delete_ids_iterator += 1
            lineitem_last_id = lineitem_id

            lineitem_new_line = "|".join([delete_ids[delete_ids_iterator]] + lineitem_rest)
            lineitem_new_lines.append(lineitem_new_line)

        with open(lineitem_file, 'w') as file:
            file.writelines(lineitem_new_lines)

    def _place_ids_from_orders_to_delete(self, orders_file, delete_file):
        with open(orders_file, 'r') as file:
            orders_lines = file.readlines()
        orders_ids = [orders_line.split('|')[0] for orders_line in orders_lines]

        delete_new_lines = [f"{order_id}|\n" for order_id in orders_ids]

        with open(delete_file, 'w') as file:
            file.writelines(delete_new_lines)
