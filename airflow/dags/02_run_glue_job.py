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
AWS_BUCKET = os.environ.get('AWS_BUCKET')
GLUE_SCRIPT_NAME = 'publish_to_snowflake.py'

logger = logging.getLogger(__name__)

# upload script
# run glue crawler
# run glue job

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

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
    dag_id='02_run_glue_job_dag',
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    start_date=datetime(2024,1,1),
) as dag:

    upload_glue_script_task = PythonOperator(
        task_id='upload_glue_script',
        python_callable=upload_file_to_s3,
        op_kwargs={
            'file_name': f"scripts/{GLUE_SCRIPT_NAME}",
            'bucket': AWS_BUCKET,
            'object_name': f"scripts/{GLUE_SCRIPT_NAME}",
        },
    )

    upload_glue_script_task