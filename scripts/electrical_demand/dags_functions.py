from electrical_demand.api.api import ForecastSMNApi, HistoricalSNMPApi, DemandByDateByRegionApi
from electrical_demand.process_data.loaders import load_historical_demand, load_holidays, load_to_db, load_file_to_s3
from electrical_demand.process_data.utils import daterange, new_rows
from electrical_demand.process_data.getters import get_csv_from_s3, get_demand, get_csv_path, get_region_dicts
from electrical_demand.ml.demand_forecast import train_and_predictions
from datetime import timedelta, datetime
from pathlib import Path
from alembic.config import Config
from alembic import command

def load_data_to_S3(general_bucket, stations_file_path, temp_forecast_stations_file_path, temp_historical_stations_file_path, historical_demand_file_path, holidays_file_path, regions_dict_file_path):
    
    load_file_to_s3(stations_file_path, general_bucket, "stations.csv")
    load_file_to_s3(temp_forecast_stations_file_path, general_bucket, "temp_forecast_stations.csv")
    load_file_to_s3(temp_historical_stations_file_path, general_bucket, "temp_historical_stations.csv")
    load_historical_demand(historical_demand_file_path, general_bucket, "historical_demand.csv")    
    load_holidays(holidays_file_path, general_bucket, "holidays.csv")
    load_file_to_s3(regions_dict_file_path, general_bucket, "region_dicts.json")

def load_raw_temp(temp_forecast_bucket, temp_historical_bucket, general_bucket, date=None, start_date=None, end_date=None):

    stations = get_csv_from_s3(general_bucket, "stations.csv")

    temp_historical_stations = get_csv_from_s3(general_bucket, "temp_historical_stations.csv")
    temp_historical_stations = temp_historical_stations.merge(stations, how="inner", on="station")
    temp_forecast_stations = get_csv_from_s3(general_bucket, "temp_forecast_stations.csv")
    temp_forecast_stations = temp_forecast_stations.merge(stations, how="inner", on="station")

    forecast_api = ForecastSMNApi(temp_forecast_bucket, temp_forecast_stations)
    historical_api = HistoricalSNMPApi(temp_historical_bucket, temp_historical_stations)

    if date != None:
        start_date = date
        end_date = date + timedelta(days=1)

    for date in daterange(start_date, end_date):
        forecast_api.etl(date)
        historical_api.etl(date)

def load_raw_demand_to_s3(date, general_bucket, demand_bucket):

    region_dicts = get_region_dicts(general_bucket)

    cammessa_api = DemandByDateByRegionApi(demand_bucket)
    cammessa_api.etl(date, region_dicts)

def load_historical_demand_to_database(client, demand_table, general_bucket, start_date, end_date):
    region_dicts = get_region_dicts(general_bucket)
    
    holidays = get_csv_from_s3(general_bucket, "holidays.csv", index_col="date", parse_dates=True)
    rows_to_add = new_rows(region_dicts, holidays, start_date, end_date=end_date)
    load_to_db(rows_to_add, demand_table, client, keep_index=True)

    historical_demand = get_csv_from_s3(general_bucket, "historical_demand.csv", index_col="datetime", parse_dates=True)
    load_to_db(historical_demand, demand_table, client, keep_index=True)

def load_demand_to_database(client, demand_table, demand_bucket, general_bucket, date):

    region_dicts = get_region_dicts(general_bucket)

    holidays = get_csv_from_s3(general_bucket, "holidays.csv", index_col="date", parse_dates=True)
    rows_to_add = new_rows(region_dicts, holidays, date)
    load_to_db(rows_to_add, demand_table, client, keep_index=True)

    csv_path = get_csv_path(date)

    demand = get_csv_from_s3(demand_bucket, csv_path, index_col="datetime", parse_dates=True)
    if demand is not None:
        load_to_db(demand, demand_table, client, keep_index=True)

def load_temp_to_database(client, demand_table, temp_forecast_bucket, temp_historical_bucket, general_bucket, date=None, start_date=None, end_date=None, delete_first_datetime=False):
    region_dicts = get_region_dicts(general_bucket)
    stations_to_demand = [region_dict["station"] for region_dict in region_dicts]

    if delete_first_datetime:
        datetime_to_delete = datetime(start_date.year, start_date.month, start_date.day)
    
    if date != None:
        start_date = date
        end_date = date + timedelta(days=1)

    for date in daterange(start_date, end_date):

        csv_path = get_csv_path(date)

        temp_historical = get_csv_from_s3(temp_historical_bucket, csv_path, index_col="datetime", parse_dates=True)
        if temp_historical is not None:
            if delete_first_datetime:
                temp_historical = temp_historical[temp_historical.index != datetime_to_delete]
            temp_historical = temp_historical[temp_historical["station"].isin(stations_to_demand)]
            temp_historical.drop(columns=["station", "file_date"], inplace=True)
            load_to_db(temp_historical, demand_table, client, keep_index=True)

        temp_forecast = get_csv_from_s3(temp_forecast_bucket, csv_path, index_col="datetime", parse_dates=True)
        if temp_forecast is not None:
            if delete_first_datetime:
                temp_forecast = temp_forecast[temp_forecast.index != datetime_to_delete]
            temp_forecast = temp_forecast[temp_forecast["station"].isin(stations_to_demand)]
            temp_forecast.drop(columns=["station", "file_date"], inplace=True)
            load_to_db(temp_forecast, demand_table, client, keep_index=True)
        
def ml_process(client, general_bucket, demand_table):
    region_dicts = get_region_dicts(general_bucket)
    for region_dict in region_dicts:
        region = region_dict["region"]
        dataset = get_demand(client, region)
        dataset.drop(columns=["region"], inplace=True)
        predictions = train_and_predictions(dataset)
        predictions["region"] = region
        load_to_db(predictions, demand_table, client, keep_index=True)

def run_migrations(dsn):
    """
    Read the table models saved in the env.py file and compares it
    with the current database model. Then generate the transition script and run it.

    Parameters
    ----------
    dsn : script
        SQLAlchemy script connection to a database
    """
    alembic_cfg = Config()
    script_location = Path(__file__).parent / "migrations"
    alembic_cfg.set_main_option("script_location", str(script_location))
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    command.revision(alembic_cfg, autogenerate=True)
    command.upgrade(alembic_cfg, "head")