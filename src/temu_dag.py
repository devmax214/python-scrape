from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from process import main
from scripts.common.constants import *

dag = DAG(
	'temu_scraper',
	description='Temu Scraper DAG',
	schedule_interval=Variable.get("temu_schedule_interval", default_var = "@hourly"),
	start_date=datetime(SCHEDULER_START_DATE[0], SCHEDULER_START_DATE[1], SCHEDULER_START_DATE[2]),
	catchup=False,
	is_paused_upon_creation=False
)

task_start = BashOperator(
	task_id = 'start_task',
	bash_command = 'echo start',
	dag = dag
)

scrapping = PythonOperator(
	task_id="run_scraper",
	python_callable=main,
 	op_kwargs={'retailer_type': str(RETAIL_TYPES['temu']), 'prefix_url': 'https://www.temu.com/'},
 	dag = dag
)

task_end = BashOperator(
	task_id = 'end_task',
	bash_command = 'echo end',
	dag = dag
)

task_start >> scrapping >> task_end
