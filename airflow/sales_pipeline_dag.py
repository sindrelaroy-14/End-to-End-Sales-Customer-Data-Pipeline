from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.models.param import Param
from datetime import datetime, timedelta

# --- Configuration ---
DATABRICKS_CONN_ID = 'databricks_default'
AWS_CONN_ID = 'aws_default'
S3_BUCKET = 'sindrela-sales-pipeline' 
# Ensure this matches the Repo path in your Databricks Workspace
REPO_PATH = '/Repos/your_user/End-to-End-Sales-Customer-Data-Pipeline/notebooks'

# Optimized Ephemeral Cluster Configuration
JOB_CLUSTER_SPEC = {
    'spark_version': '13.3.x-scala2.12',
    'node_type_id': 'i3.xlarge',
    'num_workers': 2,
    'aws_attributes': {
        'availability': 'SPOT_WITH_FALLBACK_AZ', # Saves up to 70% cost
        'ebs_volume_count': 1,
        'ebs_volume_size': 32
    }
}

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='sindrela_sales_orchestration_master',
    default_args=default_args,
    description='S3-Triggered Medallion Pipeline: Bronze -> Silver -> Gold',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    params={
        # This param is caught by dbutils.widgets.get("run_type") in your Bronze notebook
        "run_type": Param("incremental", enum=["incremental", "truncate_load"]),
    },
    tags=['sindrela', 'databricks', 'medallion']
) as dag:

    # TASK 1: S3 Sensor
    # Checks for any new CSV file in the landing-zone
    wait_for_incoming_data = S3KeySensor(
        task_id='wait_for_s3_files',
        bucket_name=S3_BUCKET,
        bucket_key='landing-zone/*.csv',
        wildcard_match=True,
        aws_conn_id=AWS_CONN_ID,
        timeout=1800,
        poke_interval=120,
        mode='reschedule' # Releases worker slot between pokes to save cost
    )

    # TASK 2: Bronze Ingestion (Truncate & Load Logic)
    task_bronze = DatabricksSubmitRunOperator(
        task_id='bronze_ingestion',
        databricks_conn_id=DATABRICKS_CONN_ID,
        new_cluster=JOB_CLUSTER_SPEC,
        notebook_task={
            'notebook_path': f'{REPO_PATH}/01_bronze_ingestion',
            'base_parameters': {
                'run_type': "{{ params.run_type }}" # Passes UI selection to Spark
            }
        }
    )

    # TASK 3: Silver CDC (History & Merge)
    task_silver = DatabricksSubmitRunOperator(
        task_id='silver_cdc_transformation',
        databricks_conn_id=DATABRICKS_CONN_ID,
        new_cluster=JOB_CLUSTER_SPEC,
        notebook_task={
            'notebook_path': f'{REPO_PATH}/02_silver_transform'
        }
    )

    # TASK 4: Gold Aggregations (BI Ready)
    task_gold = DatabricksSubmitRunOperator(
        task_id='gold_aggregations',
        databricks_conn_id=DATABRICKS_CONN_ID,
        new_cluster=JOB_CLUSTER_SPEC,
        notebook_task={
            'notebook_path': f'{REPO_PATH}/03_gold_aggregations'
        }
    )