import logging
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}'
"""Absolute path to project directory"""

LOG_LEVEL = logging.INFO
"""Message logging level"""

DB_NAME = os.getenv('MYSQL_DATABASE')
"""Defined database name from env"""

DB_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': os.getenv('MYSQL_PORT')
}
"""Defined database connection from env"""
