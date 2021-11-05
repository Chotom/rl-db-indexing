import glob
from pathlib import Path

from db_env.tpch.TpchDatabase import TpchDatabase
from shared_utils.utils import create_logger


def tpch_generator():
    """Create tables, load generated data, set indexes and relations"""
    global connection
    log = create_logger('tpch db generator')

    try:
        connection, cursor = TpchDatabase.get_connection(log, True)

        # Create tables in database
        log.info('Creating tables in database...')
        # Load file 'dss.ddl' to database
        with open(f'./tpch_tools/dbgen/dss.ddl') as ddl_file:
            sql = ddl_file.read()
            for _ in cursor.execute(sql, multi=True):
                pass

        # Load '*.tbl' files to database
        log.info('Loading data to database...')

        # temporarily disable foreign key checking
        sql = 'SET foreign_key_checks=0'
        cursor.execute(sql)

        # for each table, which is represented by '*.tbl' file
        for tbl_file in glob.glob(f'{DATA_DIR}/*.tbl'):
            # extract table name from filepath
            table_name = Path(tbl_file).stem

            log.info(f'Loading table \'{table_name}\'')

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
        log.info('Creating indexes and relations in database...')
        # Load file 'dss.ri' to database
        with open(f'{DBGEN_DIR}/dss.ri') as ri_file:
            for _ in cursor.execute(ri_file.read(), multi=True):
                pass

    except Exception as e:
        log.error(f'Exeception occured: {e}')
        return
    finally:
        connection.close()
    log.info('Database created and loaded successfully.')
