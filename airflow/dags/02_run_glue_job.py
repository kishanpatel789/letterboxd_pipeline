from pathlib import Path

import os
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

AIRFLOW_HOME = Path(os.environ.get('AIRFLOW_HOME'))
AWS_BUCKET = os.environ.get('AWS_BUCKET')
GLUE_SCRIPT_NAME = 'publish_to_snowflake.py'
GLUE_CRAWLER_NAME = 'letterboxd_crawler'
GLUE_JOB_NAME = 'publish_letterboxd_to_snowflake_tf'

logger = logging.getLogger(__name__)

def local_to_s3(file_name, key, bucket_name=AWS_BUCKET):
    s3 = S3Hook()
    s3.load_file(filename=file_name, bucket_name=bucket_name, replace=True, key=key)
    logger.info(f"File '{file_name}' uploaded to 's3://{bucket_name}/{key}'.")

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
        python_callable=local_to_s3,
        op_kwargs={
            'file_name': f"scripts/{GLUE_SCRIPT_NAME}",
            'key': f"scripts/{GLUE_SCRIPT_NAME}",
        },
    )

    run_glue_crawler_task = GlueCrawlerOperator(
        task_id='run_glue_crawler',
        aws_conn_id='aws_default',
        wait_for_completion=True,
        config={
            "Name": GLUE_CRAWLER_NAME,
        },
    )

    run_glue_job_task = GlueJobOperator(
        task_id='run_glue_job',
        job_name=GLUE_JOB_NAME,
        aws_conn_id='aws_default',
        wait_for_completion=True,
    )

    upload_glue_script_task >> run_glue_job_task
    run_glue_crawler_task >> run_glue_job_task

