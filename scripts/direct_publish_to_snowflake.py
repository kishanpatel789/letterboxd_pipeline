"""
direct_publish_to_snowflake.py

Push parquet files to Snowflake tables for dev work
"""

# %%
import snowflake.connector
from pathlib import Path
import logging

# %%
DIR_DATA = Path('../data/parquet')
STAGE_NAMESPACE = 'LETTERBOXD.RAW.RAW_STAGE'

publish_map = {
    'actors': {
        'snowflake_table': 'ACTORS',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.ACTORS; CREATE TABLE IF NOT EXISTS RAW.ACTORS (id INT, name VARCHAR);',
    },
    'countries': {
        'snowflake_table': 'COUNTRIES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.COUNTRIES; CREATE TABLE IF NOT EXISTS RAW.COUNTRIES (id INT, country VARCHAR);',
    },
    'crew': {
        'snowflake_table': 'CREW',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.CREW; CREATE TABLE IF NOT EXISTS RAW.CREW (id INT, role VARCHAR, name VARCHAR);',
    },
    'genres': {
        'snowflake_table': 'GENRES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.GENRES; CREATE TABLE IF NOT EXISTS RAW.GENRES (id INT, genre VARCHAR);',
    },
    'languages': {
        'snowflake_table': 'LANGUAGES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.LANGUAGES; CREATE TABLE IF NOT EXISTS RAW.LANGUAGES (id INT, type VARCHAR, language VARCHAR);',
    },
    'movies': {
        'snowflake_table': 'MOVIES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.MOVIES; CREATE TABLE IF NOT EXISTS RAW.MOVIES (id INT, name VARCHAR, date INT, tagline VARCHAR, description VARCHAR, minute INT, rating FLOAT);',
    },
    'releases': {
        'snowflake_table': 'RELEASES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.RELEASES; CREATE TABLE IF NOT EXISTS RAW.RELEASES (id INT, country VARCHAR, date DATE, type VARCHAR, rating VARCHAR);',
    },
    'studios': {
        'snowflake_table': 'STUDIOS',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.STUDIOS; CREATE TABLE IF NOT EXISTS RAW.STUDIOS (id INT, studio VARCHAR);',
    },
    'themes': {
        'snowflake_table': 'THEMES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.THEMES; CREATE TABLE IF NOT EXISTS RAW.THEMES (id INT, theme VARCHAR);',
    },
}

# %%
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# %%
# helper functions
def get_connection():
    try:
        conn = snowflake.connector.connect(
            connection_name='default',
            database='LETTERBOXD',
            schema='RAW',
        )
    except Exception as e:
        raise e
  
    return conn

# %%
# create snowflake stage
with get_connection() as conn:
    cursor = conn.cursor()

    cursor.execute(f'CREATE OR REPLACE STAGE {STAGE_NAMESPACE};')
    logger.info(f"Snowflake stage '{STAGE_NAMESPACE}' created.")


# %%
# upload parquet files
with get_connection() as conn:
    cursor = conn.cursor()

    for table_name in publish_map.keys():
        logger.info(f"Pushing '{table_name}'...")

        _file_name = f"{table_name}.parquet"
        _local_file_path = DIR_DATA / _file_name
        _stage_file_path = f"{STAGE_NAMESPACE}/{_file_name}"

        query = f"PUT file://{_local_file_path} @{_stage_file_path};"
        cursor.execute(query)

# %%
# copy files to snowflake tables
with get_connection() as conn:
    cursor = conn.cursor()
    
    try:
        for table_name, table_info in publish_map.items():
            logger.info(f"Copying '{table_name}'...")

            _file_name = f"{table_name}.parquet"
            _stage_file_path = f"{STAGE_NAMESPACE}/{_file_name}"

            _ddl_commands = table_info['snowflake_ddl'].split(';')
            for cmd in _ddl_commands:
                cursor.execute(cmd)

            query_copy = f"COPY INTO RAW.{table_name} FROM @{_stage_file_path} FILE_FORMAT=(TYPE=PARQUET) MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE;"
            cursor.execute(query_copy)

            logger.info(f"    Loaded '{table_name}' to RAW schema.")
    except Exception as e:
        conn.close()
        raise e


