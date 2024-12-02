from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from scripts.notifier.start_notifier import start_notifier
from scripts.common.functions import *
from scripts.common.constants import *

dag = DAG(
	'notifier_scraper',
	description='Notifer Scraper DAG',
	schedule_interval=Variable.get("notifier_schedule_interval", default_var = "@hourly"),
	start_date=datetime(SCHEDULER_START_DATE[0], SCHEDULER_START_DATE[1], SCHEDULER_START_DATE[2]),
	catchup=False,
	is_paused_upon_creation=False
)

task_start = BashOperator(
	task_id = 'start_task',
	bash_command = 'echo start',
	dag = dag
)

send_mail = PythonOperator(
	task_id = 'start_notifier',
	python_callable = start_notifier,
	dag = dag
)

task_end = BashOperator(
	task_id = 'end_task',
	bash_command = 'echo end',
	dag = dag
)

task_start >> send_mail >> task_end
