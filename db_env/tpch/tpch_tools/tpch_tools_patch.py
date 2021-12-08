import os
import shutil
from pathlib import Path
import zipfile

from db_env.tpch.config import DB_GENERATOR_TOOL

DIR_NAME = 'TPC-H_Tools_v3.0.0'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tpch_tools_patch():
    try:
        with zipfile.ZipFile(f'{parent_dir}/tpch_tools/tpc-h-tool.zip', 'r') as zip_ref:
            _extract_tpch_tools(zip_ref)
            _move_tpch_tools()
    except FileNotFoundError as e:
        print(f'Error: file not found: {e}')
    return


def _extract_tpch_tools(zip_ref: zipfile.ZipFile):
    for name in zip_ref.namelist():
        if name.startswith(DIR_NAME):
            zip_ref.extract(name, '.')


def _move_tpch_tools():
    dbgen_dir = DB_GENERATOR_TOOL

    for src_file in Path(f'{DIR_NAME}/').glob('dbgen'):
        shutil.move(src_file, f'{dbgen_dir}')
    shutil.rmtree(f'{DIR_NAME}')

    _patch(dbgen_dir)


def _patch(dbgen_dir):
    shutil.rmtree(f'{dbgen_dir}/queries')
    for src_file in Path(f'{parent_dir}/tpch_tools/dbgen_mysql_patch/').glob('*'):
        try:
            shutil.copytree(src_file, f'{dbgen_dir}/{src_file.name}')
        except NotADirectoryError:
            shutil.copy(src_file, f'{dbgen_dir}/{src_file.name}')


if __name__ == '__main__':
    tpch_tools_patch()
