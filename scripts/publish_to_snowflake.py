import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger = glueContext.get_logger()

publish_map = {
    'actors': {
        'data_catalog_table': 'actors_parquet',
        'snowflake_table': 'ACTORS',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.ACTORS; CREATE TABLE IF NOT EXISTS RAW.ACTORS (id INT, name VARCHAR);',
    },
    'countries': {
        'data_catalog_table': 'countries_parquet',
        'snowflake_table': 'COUNTRIES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.COUNTRIES; CREATE TABLE IF NOT EXISTS RAW.COUNTRIES (id INT, country VARCHAR);',
    },
    'crew': {
        'data_catalog_table': 'crew_parquet',
        'snowflake_table': 'CREW',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.CREW; CREATE TABLE IF NOT EXISTS RAW.CREW (id INT, role VARCHAR, name VARCHAR);',
    },
    'genres': {
        'data_catalog_table': 'genres_parquet',
        'snowflake_table': 'GENRES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.GENRES; CREATE TABLE IF NOT EXISTS RAW.GENRES (id INT, genre VARCHAR);',
    },
    'languages': {
        'data_catalog_table': 'languages_parquet',
        'snowflake_table': 'LANGUAGES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.LANGUAGES; CREATE TABLE IF NOT EXISTS RAW.LANGUAGES (id INT, type VARCHAR, language VARCHAR);',
    },
    'movies': {
        'data_catalog_table': 'movies_parquet',
        'snowflake_table': 'MOVIES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.MOVIES; CREATE TABLE IF NOT EXISTS RAW.MOVIES (id INT, name VARCHAR, date INT, tagline VARCHAR, description VARCHAR, minute INT, rating FLOAT);',
    },
    'releases': {
        'data_catalog_table': 'releases_parquet',
        'snowflake_table': 'RELEASES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.RELEASES; CREATE TABLE IF NOT EXISTS RAW.RELEASES (id INT, country VARCHAR, date DATE, type VARCHAR, rating VARCHAR);',
    },
    'studios': {
        'data_catalog_table': 'studios_parquet',
        'snowflake_table': 'STUDIOS',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.STUDIOS; CREATE TABLE IF NOT EXISTS RAW.STUDIOS (id INT, studio VARCHAR);',
    },
    'themes': {
        'data_catalog_table': 'themes_parquet',
        'snowflake_table': 'THEMES',
        'snowflake_ddl': 'DROP TABLE IF EXISTS RAW.THEMES; CREATE TABLE IF NOT EXISTS RAW.THEMES (id INT, theme VARCHAR);',
    },
}

for table_name, table_info in publish_map.items():
    logger.info(f"Processing '{table_name}'...")

    # read table
    dyf = (
        glueContext.create_dynamic_frame.from_catalog(
            database='letterboxd_db',
            table_name=table_info['data_catalog_table'],
        )
    )

    # push to snowflake
    glueContext.write_dynamic_frame.from_options(
        frame=dyf,
        connection_type='snowflake',
        connection_options={
            'autopushdown': 'on',
            'dbtable': table_info['snowflake_table'],
            'connectionName': 'Snowflake_Letterboxd',
            'preactions': table_info['snowflake_ddl'],
            'sfDatabase': 'LETTERBOXD',
            'sfSchema': 'RAW',
        },
    )


job.commit()
