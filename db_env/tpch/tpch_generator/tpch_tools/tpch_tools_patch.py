import shutil
from pathlib import Path
import zipfile

DIR_NAME = 'TPC-H_Tools_v3.0.0'
PATCH_DIR_NAME = 'dbgen_mysql_patch'


def tpch_tools_patch():
    try:
        with zipfile.ZipFile('tpc-h-tool.zip', 'r') as zip_ref:
            _extract_tpch_tools(zip_ref)
            _move_tpch_tools()
            _patch()
    except FileNotFoundError as e:
        print(f'Error: file not found: {e}')
    return


def _extract_tpch_tools(zip_ref: zipfile.ZipFile):
    for name in zip_ref.namelist():
        if name.startswith(DIR_NAME):
            zip_ref.extract(name, './')


def _move_tpch_tools():
    shutil.rmtree(f'./dbgen')
    for src_file in Path(f'./{DIR_NAME}/').glob('dbgen'):
        shutil.move(src_file, f'./{src_file.name}')
    shutil.rmtree(f'./{DIR_NAME}')


def _patch():
    shutil.rmtree(f'./dbgen/queries')
    for src_file in Path(f'./{PATCH_DIR_NAME}/').glob('*'):
        try:
            shutil.copytree(src_file, f'./dbgen/{src_file.name}')
        except NotADirectoryError:
            shutil.copy(src_file, f'./dbgen/{src_file.name}')


if __name__ == '__main__':
    tpch_tools_patch()
