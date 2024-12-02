#!/bin/bash
# export AIRFLOW_HOME=~/Workspace/DIY/Airflow
export AIRFLOW_HOME=~/Public/webscrape/airflow
# This script will set Airflow Schedule Variables
airflow variables set amazon_schedule_interval @hourly
airflow variables set cashback_schedule_interval @hourly
airflow variables set nike_schedule_interval @hourly
airflow variables set rei_schedule_interval @hourly
airflow variables set target_schedule_interval @hourly
airflow variables set huckberry_schedule_interval @hourly
airflow variables set shein_schedule_interval @hourly
airflow variables set temu_schedule_interval @hourly
airflow variables set chrono24_schedule_interval @hourly
airflow variables set bestbuy_schedule_interval @hourly
airflow variables set wayfair_schedule_interval @hourly
airflow variables set notifier_schedule_interval @hourly