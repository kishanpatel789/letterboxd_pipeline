from cosmos.config import ProfileConfig
from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
import os
import logging 
from pathlib import Path
from datetime import datetime

AIRFLOW_HOME = Path(os.environ.get('AIRFLOW_HOME'))

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

project_config = ProjectConfig(
    f"{AIRFLOW_HOME}/dbt",
)

profile_config = ProfileConfig(
    profile_name="snowflake_letterboxd",
    target_name="dev",
    profiles_yml_filepath="/home/airflow/.dbt/profiles.yml",
)

execution_config = ExecutionConfig(
    dbt_executable_path="/home/airflow/.local/bin/dbt",
)

my_cosmos_dag = DbtDag(
    project_config=project_config,
    profile_config=profile_config,
    execution_config=execution_config,
    # normal dag parameters
    dag_id="03_run_dbt_dag",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    start_date=datetime(2024,1,1),
)


