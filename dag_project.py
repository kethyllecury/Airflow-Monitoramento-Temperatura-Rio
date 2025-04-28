from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from datetime import datetime, timedelta
import json
import os

def extract_temp_data(**kwargs):
    with open(Variable.get('simple_temp_file_path')) as f:
        data = json.load(f)
        ti = kwargs['ti']
        ti.xcom_push(key='river_id', value=data['river_id'])
        ti.xcom_push(key='temperature', value=data['temperature'])
        ti.xcom_push(key='timestamp', value=data['timestamp'])
    os.remove(Variable.get('simple_temp_file_path'))

def check_temperature(**context):
    temp = float(context['ti'].xcom_pull(task_ids='extract_data', key='temperature'))
    return 'group_email.temp_alert_email' if temp < 10 or temp > 25 else 'group_email.temp_ok_email'


default_args = {
    'email': ['kethyllecury@gmail.com'],
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

dag = DAG(
    'simple_river_temp_monitoring',
    description='Monitoramento simples da temperatura do rio',
    schedule_interval=None,
    start_date=datetime(2023, 3, 5),
    catchup=False,
    default_args=default_args
)


group_email = TaskGroup("group_email", dag=dag)
group_db = TaskGroup("group_db", dag=dag)


sensor = FileSensor(
    task_id='wait_for_file',
    filepath=Variable.get('simple_temp_file_path'),
    fs_conn_id='fs_default',
    poke_interval=10,
    timeout=30,
    dag=dag
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_temp_data,
    provide_context=True,
    dag=dag
)


create_table = PostgresOperator(
    task_id='create_temp_table',
    postgres_conn_id='postgres',
    sql='''
    CREATE TABLE IF NOT EXISTS river_temperature (
        river_id VARCHAR,
        temperature FLOAT,
        timestamp VARCHAR
    );
    ''',
    task_group=group_db,
    dag=dag
)


insert_task = PostgresOperator(
    task_id='insert_temp_data',
    postgres_conn_id='postgres',
    parameters=(
        '{{ ti.xcom_pull(task_ids="extract_data", key="river_id") }}',
        '{{ ti.xcom_pull(task_ids="extract_data", key="temperature") }}',
        '{{ ti.xcom_pull(task_ids="extract_data", key="timestamp") }}'
    ),
    sql='''
    INSERT INTO river_temperature (river_id, temperature, timestamp)
    VALUES (%s, %s, %s);
    ''',
    task_group=group_db,
    dag=dag
)


alert_email = EmailOperator(
    task_id='temp_alert_email',
    to='kethyllecury@gmail.com',
    subject='Alerta de Temperatura',
    html_content='<h3>Temperatura fora do limite!</h3>',
    task_group=group_email,
    dag=dag
)

ok_email = EmailOperator(
    task_id='temp_ok_email',
    to='kethyllecury@gmail.com',
    subject='Temperatura Normal',
    html_content='<h3>Temperatura dentro do limite.</h3>',
    task_group=group_email,
    dag=dag
)


branch = BranchPythonOperator(
    task_id='check_temp',
    python_callable=check_temperature,
    provide_context=True,
    task_group=group_email,
    dag=dag
)


sensor >> extract_task
extract_task >> group_db
extract_task >> group_email

with group_db:
    create_table >> insert_task

with group_email:
    branch >> [alert_email, ok_email]
