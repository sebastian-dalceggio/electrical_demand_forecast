from airflow.decorators import dag
from datetime import timedelta, date
import pendulum
from config import DATABASE_STRING, DATABASE_TYPE, DATABASE_NAME, DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, TEMP_FORECAST_BUCKET_NAME, TEMP_HISTORICAL_BUCKET_NAME, GENERAL_BUCKET_NAME, DEMAND_BUCKET_NAME
from tasks import upgrade_tables, load_to_s3, load_to_database, run_machine_learning, load_new_to_s3, load_new_to_database

@dag(
    schedule=None,
    start_date=pendulum.datetime(2022, 11, 1, 1, 0, 0, tz="America/Argentina/Buenos_Aires"),
    catchup=True,
    max_active_runs=1,
)
def data_preparation_dag(database_string, database_type, database_name, database_host, database_user, database_password, general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date):

    upgrade_tables_r = upgrade_tables(database_string)
    load_to_s3_r = load_to_s3(general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date)
    load_to_database_r = load_to_database(database_type, database_name, database_host, database_user, database_password, general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date)
    run_machine_learning_r = run_machine_learning(database_type, database_name, database_host, database_user, database_password, general_bucket)

    upgrade_tables_r >> load_to_s3_r >> load_to_database_r >> run_machine_learning_r

@dag(
    schedule=timedelta(days=1),
    start_date=pendulum.datetime(2022, 11, 2, 1, 0, 0, tz="America/Argentina/Buenos_Aires"),
    catchup=True,
    max_active_runs=1,
)
def new_data_dag(database_string, database_type, database_name, database_host, database_user, database_password, demand_bucket, general_bucket, temp_forecast_bucket, temp_historical_bucket):

    upgrade_tables_r = upgrade_tables(database_string)
    load_new_to_s3_r = load_new_to_s3(general_bucket, demand_bucket, temp_forecast_bucket, temp_historical_bucket, "{{ ds }}")
    load_new_to_database_r = load_new_to_database(database_type, database_name, database_host, database_user, database_password, demand_bucket, general_bucket, temp_forecast_bucket, temp_historical_bucket, "{{ ds }}")
    run_machine_learning_r = run_machine_learning(database_type, database_name, database_host, database_user, database_password, general_bucket)

    upgrade_tables_r >> load_new_to_s3_r >> load_new_to_database_r >> run_machine_learning_r


start_date = date(2019,1,1)
end_date = date(2022,11,1)
temp_forecast_bucket = TEMP_FORECAST_BUCKET_NAME
temp_historical_bucket = TEMP_HISTORICAL_BUCKET_NAME
general_bucket = GENERAL_BUCKET_NAME
demand_bucket = DEMAND_BUCKET_NAME
database_string = DATABASE_STRING
database_type = DATABASE_TYPE
database_name = DATABASE_NAME
database_host = DATABASE_HOST
database_user = DATABASE_USER
database_password = DATABASE_PASSWORD

data_preparation_dag(database_string, database_type, database_name, database_host, database_user, database_password, general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date)
new_data_dag(database_string, database_type, database_name, database_host, database_user, database_password, demand_bucket, general_bucket, temp_forecast_bucket, temp_historical_bucket)