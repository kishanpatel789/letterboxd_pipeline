import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq

from pathlib import Path

import os
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

AIRFLOW_HOME = Path(os.environ.get('AIRFLOW_HOME'))
DIR_DATA = AIRFLOW_HOME / 'data'
AWS_BUCKET = os.environ.get('AWS_BUCKET')

logger = logging.getLogger(__name__)

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
def convert_to_parquet(ingestion_map):
    for table_name, table_info in ingestion_map.items():
        logger.info(f"Converting '{table_name}'...")

        table = pv.read_csv(DIR_DATA / 'csv' / table_info['csv_file_name'])
        table = table.cast(table_info['schema'])
        pq.write_table(table, DIR_DATA / 'parquet' / table_info['parquet_file_name'])

        logger.info(f"    '{table_info['csv_file_name']}' converted to '{table_info['parquet_file_name']}'")
        logger.info(f"    {table.num_rows:,} records")

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

def upload_parquet_files(ingestion_map):
    for table_name, table_info in ingestion_map.items():
        logger.info(f"Pushing '{table_name}'...")

        _local_file_path = DIR_DATA / 'parquet' / table_info['parquet_file_name']
        _s3_file_key = f"raw/{table_info['parquet_file_name']}"

        upload_file_to_s3(_local_file_path, AWS_BUCKET, _s3_file_key)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
    dag_id='01_ingest_data_dag',
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    start_date=datetime(2024,1,1),
) as dag:

    create_data_directory_task = BashOperator(
        task_id='create_data_directory',
        bash_command=f'cd {AIRFLOW_HOME} && mkdir -p data/csv data/parquet'
    )

    extract_csv_files_task = BashOperator(
        task_id='extract_csv_files',
        bash_command=f"""cd {AIRFLOW_HOME}/raw_data_archive && \
            unzip -o archive.zip \
            actors.csv countries.csv crew.csv genres.csv languages.csv movies.csv releases.csv studios.csv themes.csv  \
            -d ../data/csv/ && \
            cd {AIRFLOW_HOME}/data/csv/"""
    )

    convert_to_parquet_task = PythonOperator(
        task_id='convert_to_parquet',
        python_callable=convert_to_parquet,
        op_kwargs=dict(ingestion_map=ingestion_map)
    )

    upload_parquet_files_task = PythonOperator(
        task_id='upload_parquet_files',
        python_callable=upload_parquet_files,
        op_kwargs=dict(ingestion_map=ingestion_map)
    )

    local_cleanup_task = BashOperator(
        task_id='local_cleanup',
        bash_command=f"cd {AIRFLOW_HOME} && rm -r data/"
    )

    create_data_directory_task >> extract_csv_files_task >> convert_to_parquet_task >> \
        upload_parquet_files_task >> local_cleanup_task
