from airflow.decorators import task
from docker.types import Mount
from config import PROJECT_DIR, DEMAND_DOCKER_IMAGE

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
    mounts=[
        Mount(
            source=f"{PROJECT_DIR}/versions",
            target="/usr/local/lib/python3.8/site-packages/electrical_demand/migrations/versions",
            type="bind",
        ),
    ],
)
def upgrade_tables(database_string):
    from electrical_demand.dags_functions import run_migrations
    run_migrations(database_string)

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
    mounts=[
        Mount(source=f"{PROJECT_DIR}/data", target="/root/data", type="bind"),
    ],
)
def load_to_s3(general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date):
    from electrical_demand.dags_functions import load_data_to_S3, load_raw_temp
    
    stations_file_path = "root/data/stations.csv"
    temp_forecast_stations_file_path = "root/data/temp_forecast_stations.csv"
    temp_historical_stations_file_path = "root/data/temp_historical_stations.csv"
    historical_demand_file_path = "root/data/historical_demand_by_province.xlsx"
    holidays_file_path = "root/data/holidays.csv"
    regions_dict_file_path = "root/data/regions.json"

    load_data_to_S3(general_bucket, stations_file_path, temp_forecast_stations_file_path, temp_historical_stations_file_path, historical_demand_file_path, holidays_file_path, regions_dict_file_path)
    load_raw_temp(temp_forecast_bucket, temp_historical_bucket, general_bucket, start_date=start_date, end_date=end_date)

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
)
def load_to_database(database_type, database_name, database_host, database_user, database_password, general_bucket, temp_forecast_bucket, temp_historical_bucket, start_date, end_date):
    from electrical_demand.database.client import ComplexClient
    from electrical_demand.database.models import Demand
    from electrical_demand.dags_functions import load_historical_demand_to_database, load_temp_to_database
    
    demand_table = Demand
    client = ComplexClient(database_type, database_name, database_host, database_user, database_password)

    load_historical_demand_to_database(client, demand_table, general_bucket, start_date, end_date)
    load_temp_to_database(client, demand_table, temp_forecast_bucket, temp_historical_bucket, general_bucket, start_date=start_date, end_date=end_date, delete_first_datetime=True)

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
)
def run_machine_learning(database_type, database_name, database_host, database_user, database_password, general_bucket):
    from electrical_demand.dags_functions import ml_process
    from electrical_demand.database.client import ComplexClient
    from electrical_demand.database.models import Demand

    client = ComplexClient(database_type, database_name, database_host, database_user, database_password)
    demand_table = Demand

    ml_process(client, general_bucket, demand_table)

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
)
def load_new_to_s3(general_bucket, demand_bucket, temp_forecast_bucket, temp_historical_bucket, current_date):
    from electrical_demand.dags_functions import load_raw_demand_to_s3, load_raw_temp
    from electrical_demand.process_data.utils import get_new_data_date

    new_data_date = get_new_data_date(current_date)
    load_raw_demand_to_s3(new_data_date, general_bucket, demand_bucket)
    load_raw_temp(temp_forecast_bucket, temp_historical_bucket, general_bucket, date=new_data_date)

@task.docker(
    image=DEMAND_DOCKER_IMAGE,
    mount_tmp_dir=False,
)
def load_new_to_database(database_type, database_name, database_host, database_user, database_password, demand_bucket, general_bucket, temp_forecast_bucket, temp_historical_bucket, current_date):
    from electrical_demand.dags_functions import load_demand_to_database, load_temp_to_database
    from electrical_demand.database.client import ComplexClient
    from electrical_demand.database.models import Demand
    from electrical_demand.process_data.utils import get_new_data_date

    client = ComplexClient(database_type, database_name, database_host, database_user, database_password)
    demand_table = Demand
    new_data_date = get_new_data_date(current_date)

    load_demand_to_database(client, demand_table, demand_bucket, general_bucket, new_data_date)
    load_temp_to_database(client, demand_table, temp_forecast_bucket, temp_historical_bucket, general_bucket, date=new_data_date)

