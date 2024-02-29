"""
local_processing.py

Convert csv files to parquet and push to S3
"""

# %%
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq

from pathlib import Path

import logging
import boto3
from botocore.exceptions import ClientError
import os

# %%
DIR_DATA = Path('../data')
AWS_BUCKET = 'letterboxd-data-kpde'

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
ingestion_map = {
    'actors': {
        'csv_file_name': 'actors.csv',
        'parquet_file_name': 'actors.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('name', pa.string()),
        ]),
    },
    'countries': {
        'csv_file_name': 'countries.csv',
        'parquet_file_name': 'countries.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('country', pa.string()),
        ]),
    },
    'crew': {
        'csv_file_name': 'crew.csv',
        'parquet_file_name': 'crew.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('role', pa.string()),
            ('name', pa.string()),
        ]),
    },
    'genres': {
        'csv_file_name': 'genres.csv',
        'parquet_file_name': 'genres.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('genre', pa.string()),
        ]),
    },
    'languages': {
        'csv_file_name': 'languages.csv',
        'parquet_file_name': 'languages.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('type', pa.string()),
            ('language', pa.string()),
        ]),
    },
    'movies': {
        'csv_file_name': 'movies.csv',
        'parquet_file_name': 'movies.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('name', pa.string()),
            ('date', pa.int32()),
            ('tagline', pa.string()),
            ('description', pa.string()),
            ('minute', pa.int64()),
            ('rating', pa.float32()),
        ]),
    },
    'releases': {
        'csv_file_name': 'releases.csv',
        'parquet_file_name': 'releases.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('country', pa.string()),
            ('date', pa.date32()),
            ('type', pa.string()),
            ('rating', pa.string()),
        ]),
    },
    'studios': {
        'csv_file_name': 'studios.csv',
        'parquet_file_name': 'studios.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('studio', pa.string()),
        ]),
    },
    'themes': {
        'csv_file_name': 'themes.csv',
        'parquet_file_name': 'themes.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('theme', pa.string()),
        ]),
    },
}
# %%
# convert csv to parquet
for table_name, table_info in ingestion_map.items():
    logger.info(f"Converting '{table_name}'...")

    table = pv.read_csv(DIR_DATA / 'csv' / table_info['csv_file_name'])
    table = table.cast(table_info['schema'])
    pq.write_table(table, DIR_DATA / 'parquet' / table_info['parquet_file_name'])

    logger.info(f"    '{table_info['csv_file_name']}' converted to '{table_info['parquet_file_name']}'")
    logger.info(f"    {table.num_rows:,} records")


# %%
# push parquet files to s3
def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    Modified from https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(str(file_name), bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True

for table_name, table_info in ingestion_map.items():
    logger.info(f"Pushing '{table_name}'...")

    _local_file_path = DIR_DATA / 'parquet' / table_info['parquet_file_name']
    _s3_file_key = f"raw/{table_info['parquet_file_name']}"

    upload_file_to_s3(_local_file_path, AWS_BUCKET, _s3_file_key)


# %%
